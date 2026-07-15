import { Component, EventEmitter, Output, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

export interface ClientProfileForm {
  Age: number | null;
  Ville: string;
  Profession: string;
  Usage: string;
  Kilometrage: number | null;
  GarageFerme: string; // 'True' | 'False'
  Marque: string;
  Categorie: string;
  Carburant: string;
  PuissanceCV: number | null;
  BonusMalus: number | null;
  NombreSinistres5Ans: number | null;
  AncienneteClient: number | null;
  budget: number | null;
}

@Component({
  selector: 'app-pack-form',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './pack-form.html',
  styleUrl: './pack-form.css'
})
export class PackForm {
  @Output() formSubmit = new EventEmitter<ClientProfileForm>();
  @Output() formCancel = new EventEmitter<void>();

  villes = ['Casablanca', 'Rabat', 'Marrakech', 'Fès', 'Tanger', 'Agadir', 'Meknès', 'Oujda', 'Kénitra', 'Tétouan', 'Salé', 'Nador', 'Mohammedia', 'El Jadida', 'Beni Mellal', 'Khouribga', 'Settat', 'Laâyoune', 'Errachidia', 'Essaouira'];
  professions = ['Employé de bureau', 'Cadre supérieur', 'Médecin', 'Avocat', 'Commerçant', 'Artisan', 'Enseignant', 'Fonctionnaire', 'Ingénieur', 'Infirmier', 'Chauffeur VTC', 'Chauffeur taxi', 'Étudiant', 'Retraité', 'Agriculteur', 'Technicien', 'Comptable', 'Architecte', 'Pharmacien', 'Sans emploi'];
  usages = ['Privé', 'Privé-Travail', 'Professionnel', 'VTC/Taxi'];
  marques = ['Renault', 'Dacia', 'Peugeot', 'Toyota', 'Hyundai', 'Volkswagen', 'BMW', 'Mercedes-Benz', 'Kia', 'Citroën', 'Nissan', 'Suzuki', 'Audi', 'Fiat', 'Ford'];
  categories = ['Citadine', 'Compacte', 'Berline', 'SUV', 'Pick-up'];
  carburants = ['Essence', 'Diesel', 'Hybride', 'Électrique'];

  profile = signal<ClientProfileForm>({
    Age: null,
    Ville: '',
    Profession: '',
    Usage: '',
    Kilometrage: null,
    GarageFerme: 'False',
    Marque: '',
    Categorie: '',
    Carburant: '',
    PuissanceCV: null,
    BonusMalus: 1.0,
    NombreSinistres5Ans: 0,
    AncienneteClient: 0,
    budget: null
  });

  updateField<K extends keyof ClientProfileForm>(field: K, value: ClientProfileForm[K]) {
    this.profile.update(p => ({ ...p, [field]: value }));
  }

  isValid(): boolean {
    const p = this.profile();
    return !!(p.Age && p.Ville && p.Profession && p.Usage && p.Kilometrage && p.Marque && p.Categorie && p.Carburant && p.PuissanceCV);
  }

  submit() {
    if (!this.isValid()) return;
    this.formSubmit.emit(this.profile());
  }

  cancel() {
    this.formCancel.emit();
  }
}