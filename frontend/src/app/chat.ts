import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ClientProfileForm } from './pack-form/pack-form';

export interface ChatResponse {
  answer: string;
}

export interface WelcomeOption {
  id: string;
  label: string;
}

export interface WelcomeResponse {
  message: string;
  options: WelcomeOption[];
}

export interface PackCard {
  PackID: string;
  Nom: string;
  Segment: string;
  PrixBase: number;
  EstimatedPrice: number;
  CoverageCount: number;
  GarantiesIncluses: string[];
  LimiteKilometrique: number;
  Franchise: number;
  Eligible: boolean;
  FitScore: number;
  Description: string;
}

export interface RecommendationResponse {
  cards: PackCard[];
  recommended_pack_id: string;
  recommendation_text: string;
}

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private baseUrl = 'http://localhost:8000';
  public sessionId: string = crypto.randomUUID();

  constructor(private http: HttpClient) {}

  getWelcome(): Observable<WelcomeResponse> {
    return this.http.get<WelcomeResponse>(`${this.baseUrl}/welcome`);
  }

  sendMessage(query: string): Observable<ChatResponse> {
    return this.http.post<ChatResponse>(`${this.baseUrl}/chat`, {
      session_id: this.sessionId,
      query
    });
  }

  getRecommendation(profile: ClientProfileForm): Observable<RecommendationResponse> {
    return this.http.post<RecommendationResponse>(`${this.baseUrl}/recommend-packs`, profile);
  }
}