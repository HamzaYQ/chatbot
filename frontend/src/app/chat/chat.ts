import { Component, signal, OnInit, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { ChatService, PackCard } from '../chat';
import { PackForm, ClientProfileForm } from '../pack-form/pack-form';
import { PackResults } from '../pack-results/pack-results';

interface Message {
  role: 'user' | 'bot';
  type: 'text' | 'packs';
  text: string;
  html?: SafeHtml;
  time: string;
  packsData?: {
    cards: PackCard[];
    recommendedPackId: string;
    recommendationText: string;
  };
}

interface SuggestedAction {
  label: string;
  query?: string;
  action?: 'form'; // si présent, ouvre le formulaire au lieu d'envoyer une requête chat
}

const DEFAULT_SUGGESTIONS: SuggestedAction[] = [
  { label: 'Déclarer un sinistre', query: 'Comment déclarer un sinistre ?' },
  { label: 'Suivre mon dossier', query: 'Comment suivre mon dossier de sinistre ?' },
  { label: 'Choisir un pack', action: 'form' },
  { label: 'Simuler un devis', query: 'Je veux simuler un devis' },
  { label: 'Mon contrat', query: 'Je veux consulter mon contrat' },
];

const WELCOME_MESSAGE =
  "Bonjour ! Bienvenue chez Sanlam Allianz, je suis votre asssiant virtuel. Comment puis-je vous aider aujourd'hui ? 😊";

@Component({
  selector: 'app-chat',
  imports: [FormsModule, PackForm, PackResults],
  templateUrl: './chat.html',
})
export class Chat implements OnInit, AfterViewChecked {
  @ViewChild('messagesContainer') messagesContainer!: ElementRef<HTMLDivElement>;

  messages = signal<Message[]>([]);
  userInput = signal('');
  loading = signal(false);
  suggestedActions = signal<SuggestedAction[]>(DEFAULT_SUGGESTIONS);
  showPackForm = signal(false);

  constructor(
    private chatService: ChatService,
    private sanitizer: DomSanitizer,
  ) {}

  ngOnInit(): void {
    this.messages.set([]);
    this.typeBotMessage(WELCOME_MESSAGE);
  }
  private scrollTargetIndex: number | null = null;

  ngAfterViewChecked(): void {
    if (this.scrollTargetIndex !== null) {
      this.scrollToMessage(this.scrollTargetIndex);
      this.scrollTargetIndex = null;
    }
  }

  private scrollToMessage(index: number): void {
    try {
      const container = this.messagesContainer.nativeElement;
      const el = container.querySelector<HTMLElement>(`#msg-${index}`);
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    } catch {
      /* ignore si pas encore rendu */
    }
  }

  private scrollToLastUserMessage(): void {
    this.scrollTargetIndex = this.messages().length - 1;
  }

  private formatText(text: string): SafeHtml {
    let html = text
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/(\d+)\.\s+\*\*/g, '<br>$1. <strong>')
      .replace(/\n/g, '<br>');
    return this.sanitizer.bypassSecurityTrustHtml(html);
  }
  private typeBotMessage(fullText: string, onComplete?: () => void): void {
    const msg = this.buildMessage('bot', fullText);
    msg.html = this.sanitizer.bypassSecurityTrustHtml('');
    this.messages.update((msgs) => [...msgs, msg]);

    const chunkSize = 3; // nb de caractères ajoutés à chaque tick
    const intervalMs = 20; // vitesse (plus petit = plus rapide)
    let index = 0;

    const interval = setInterval(() => {
      index += chunkSize;
      msg.html = this.formatText(fullText.slice(0, index));
      this.messages.update((msgs) => [...msgs]);

      if (index >= fullText.length) {
        clearInterval(interval);
        onComplete?.();
      }
    }, intervalMs);
  }

  private buildMessage(
    role: 'user' | 'bot',
    text: string,
    type: 'text' | 'packs' = 'text',
    packsData?: Message['packsData'],
  ): Message {
    const time = new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
    return {
      role,
      text,
      time,
      type,
      packsData,
      html: role === 'bot' && type === 'text' ? this.formatText(text) : undefined,
    };
  }

  sendSuggestion(action: SuggestedAction) {
    if (this.loading()) return;

    if (action.action === 'form') {
      this.suggestedActions.set([]);
      this.messages.update((msgs) => [
        ...msgs,
        this.buildMessage('user', 'Je veux choisir les packs adaptés à mon profil'),
      ]);
      this.scrollToLastUserMessage();

      this.typeBotMessage('Avec plaisir. Pour vous proposer les packs adaptés à votre profil, merci de renseigner quelques informations dans le formulaire ci-dessous.', () => {
        this.showPackForm.set(true);
      });
      return;
    }

    this.suggestedActions.set([]);
    this.sendQuery(action.query!, action.query!);
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
    this.messages.update((msgs) => [...msgs, this.buildMessage('user', displayText)]);
    this.loading.set(true);
    this.scrollToLastUserMessage();

    this.chatService.sendMessage(query).subscribe({
      next: (res) => {
        this.loading.set(false);
        this.typeBotMessage(res.answer);
      },
      error: (err) => {
        const message =
          err.status === 429
            ? 'Le service est temporairement surchargé. Merci de réessayer dans quelques minutes.'
            : 'Erreur : impossible de contacter le serveur. Veuillez réessayer.';
        this.messages.update((msgs) => [...msgs, this.buildMessage('bot', message)]);
        this.loading.set(false);
      },
    });
  }

  onPackFormSubmit(profile: ClientProfileForm) {
    this.showPackForm.set(false);
    this.loading.set(true);

    this.chatService.getRecommendation(profile).subscribe({
      next: (res) => {
        this.messages.update((msgs) => [
          ...msgs,
          this.buildMessage('bot', '', 'packs', {
            cards: res.cards,
            recommendedPackId: res.recommended_pack_id,
            recommendationText: res.recommendation_text,
          }),
        ]);
        this.loading.set(false);
      },
      error: () => {
        this.messages.update((msgs) => [
          ...msgs,
          this.buildMessage('bot', 'Erreur lors du calcul de la recommandation.'),
        ]);
        this.loading.set(false);
      },
    });
  }

  onPackFormCancel() {
    this.showPackForm.set(false);
    this.messages.update((msgs) => [...msgs, this.buildMessage('bot', 'Formulaire annulé.')]);
  }
}
