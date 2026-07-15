import { Component, Input } from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { PackCard } from '../chat';

@Component({
  selector: 'app-pack-results',
  standalone: true,
  imports: [DecimalPipe],
  templateUrl: './pack-results.html',
  styleUrl: './pack-results.css'
})
export class PackResults {
  @Input() cards: PackCard[] = [];
  @Input() recommendedPackId: string = '';
  @Input() recommendationText: string = '';
}