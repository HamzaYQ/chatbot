import { Component, signal, OnInit, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { ChatService } from '../chat';

interface Message {
  role: 'user' | 'bot';
  text: string;
  html?: SafeHtml;
  time: string;
  isLong?: boolean;
  expanded?: boolean;

}

interface SuggestedAction {
  label: string;
  query: string;
}

const DEFAULT_SUGGESTIONS: SuggestedAction[] = [
  { label: 'Déclarer un sinistre', query: 'Comment déclarer un sinistre ?' },
  { label: 'Suivre mon dossier', query: 'Comment suivre mon dossier de sinistre ?' },
  { label: 'Choisir un pack', query: 'Quels sont les packs d\'assurance disponibles ?' },
  { label: 'Simuler un devis', query: 'Je veux simuler un devis' },
  { label: 'Mon contrat', query: 'Je veux consulter mon contrat' }
];

const WELCOME_MESSAGE = 'Bonjour ! Bienvenue chez AssurAuto Maroc. Comment puis-je vous aider aujourd\'hui ?';

@Component({
  selector: 'app-chat',
  imports: [FormsModule],
  templateUrl: './chat.html',
  styleUrl: './chat.css'
})
export class Chat implements OnInit, AfterViewChecked {
  @ViewChild('messagesContainer') messagesContainer!: ElementRef<HTMLDivElement>;

  messages = signal<Message[]>([]);
  userInput = signal('');
  loading = signal(false);
  suggestedActions = signal<SuggestedAction[]>(DEFAULT_SUGGESTIONS);

  private readonly TRUNCATE_LENGTH = 350;
  private shouldScroll = false;

  constructor(
    private chatService: ChatService,
    private sanitizer: DomSanitizer
  ) {}

  ngOnInit(): void {
    this.messages.set([this.buildMessage('bot', WELCOME_MESSAGE)]);
  }

  ngAfterViewChecked(): void {
    if (this.shouldScroll) {
      this.scrollToBottom();
      this.shouldScroll = false;
    }
  }

  private scrollToBottom(): void {
    try {
      const el = this.messagesContainer.nativeElement;
      el.scrollTop = el.scrollHeight;
    } catch { /* ignore si pas encore rendu */ }
  }

  private formatText(text: string): SafeHtml {
    let html = text
      .replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/(\d+)\.\s+\*\*/g, '<br>$1. <strong>')
      .replace(/\n/g, '<br>');
    return this.sanitizer.bypassSecurityTrustHtml(html);
  }

  private buildMessage(role: 'user' | 'bot', text: string): Message {
    const time = new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
    const isLong = role === 'bot' && text.length > this.TRUNCATE_LENGTH;
    return {
      role,
      text,
      time,
      isLong,
      expanded: false,
      html: role === 'bot' ? this.formatText(text) : undefined
    };
  }

  // Retourne le HTML tronqué ou complet selon l'état "expanded"
  getDisplayHtml(msg: Message): SafeHtml {
    if (!msg.isLong || msg.expanded) {
      return msg.html!;
    }
    const truncated = msg.text.slice(0, this.TRUNCATE_LENGTH) + '...';
    return this.formatText(truncated);
  }

  toggleExpand(msg: Message): void {
    msg.expanded = !msg.expanded;
    this.messages.update(msgs => [...msgs]);
  }

  sendSuggestion(action: SuggestedAction) {
    if (this.loading()) return;
    this.suggestedActions.set([]);
    this.sendQuery(action.query, action.label);
  }

  send() {
    if (this.loading()) return;
    const query = this.userInput().trim();
    if (!query) return;
    this.suggestedActions.set([]);
    this.userInput.set('');
    this.sendQuery(query, query);
  }

 
  private sendQuery(query: string, displayText: string) {
    this.messages.update(msgs => [...msgs, this.buildMessage('user', displayText)]);
    this.loading.set(true);
    this.shouldScroll = true;

    this.chatService.sendMessage(query).subscribe({
      next: (res) => {
        this.messages.update(msgs => [...msgs, this.buildMessage('bot', res.answer)]);
        this.loading.set(false);
        this.shouldScroll = true;
      },
      error: (err) => {
        const message = err.status === 429
          ? "Le service est temporairement surchargé. Merci de réessayer dans quelques minutes."
          : "Erreur : impossible de contacter le serveur. Veuillez réessayer.";
        this.messages.update(msgs => [...msgs, this.buildMessage('bot', message)]);
        this.loading.set(false);
        this.shouldScroll = true;
      }
    });
  }
}