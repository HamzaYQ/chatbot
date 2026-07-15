"""
pricing_engine.py

Moteur de scoring/recommandation de packs pour AssurAuto Maroc.
Combine packs.csv + pricing_rules.csv + pack_eligibility.csv (données structurées,
pas de LLM) pour produire un classement objectif de packs adaptés à un profil client.

Le LLM n'intervient PAS ici — il sert uniquement, en aval, à formuler l'explication
en langage naturel à partir du résultat retourné par `recommend_packs`.
"""

import csv
import re
from pathlib import Path
from typing import Any, Optional


# ----------------------------------------------------------------------
# Chargement des données
# ----------------------------------------------------------------------

def _read_csv(path: str) -> list[dict]:
    with open(path, encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


GARANTIE_COLUMNS = [
    'ResponsabiliteCivile', 'Vol', 'Incendie', 'BrisDeGlace',
    'CatastrophesNaturelles', 'DommagesCollision', 'TousRisques',
    'Assistance', 'Remorquage', 'VehiculeRemplacement',
    'ProtectionConducteur', 'ProtectionJuridique'
]

# Noms lisibles pour l'affichage dans les cartes (plutôt que les noms de colonnes bruts)
GARANTIE_LABELS = {
    'ResponsabiliteCivile': 'Responsabilité civile',
    'Vol': 'Vol',
    'Incendie': 'Incendie',
    'BrisDeGlace': 'Bris de glace',
    'CatastrophesNaturelles': 'Catastrophes naturelles',
    'DommagesCollision': 'Dommages collision',
    'TousRisques': 'Tous risques',
    'Assistance': 'Assistance',
    'Remorquage': 'Remorquage',
    'VehiculeRemplacement': 'Véhicule de remplacement',
    'ProtectionConducteur': 'Protection conducteur',
    'ProtectionJuridique': 'Protection juridique',
}


def load_packs(path: str) -> list[dict]:
    rows = _read_csv(path)
    for row in rows:
        row['PrixBase'] = float(row['PrixBase'])
        row['LimiteKilometrique'] = int(row['LimiteKilometrique'])
        row['Franchise'] = float(row['Franchise'])
        included = [col for col in GARANTIE_COLUMNS if int(row[col]) == 1]
        row['_coverage_count'] = len(included)
        row['_garanties_incluses'] = [GARANTIE_LABELS[col] for col in included]
    return rows


def load_eligibility(path: str) -> dict[str, dict]:
    rows = _read_csv(path)
    eligibility = {}
    for row in rows:
        row['UsageRecommande'] = [u.strip() for u in row['UsageRecommande'].split(';')]
        row['AgeMinConducteur'] = int(row['AgeMinConducteur'])
        eligibility[row['PackID']] = row
    return eligibility


CONDITION_RE = re.compile(r'^([A-Za-zÀ-ÿ0-9]+)(>=|<=|>|<|=)(.+)$')


def load_rules(path: str) -> dict[str, list[dict]]:
    """Charge pricing_rules.csv et regroupe les règles par champ (Age, Ville, ...)."""
    rows = _read_csv(path)
    rules_by_field: dict[str, list[dict]] = {}

    for row in rows:
        match = CONDITION_RE.match(row['Condition'])
        if not match:
            print(f"[WARN] Condition non reconnue, ignorée: {row['Condition']}")
            continue
        field, operator, raw_value = match.groups()
        rules_by_field.setdefault(field, []).append({
            'operator': operator,
            'value': raw_value,
            'coefficient': float(row['Coefficient']),
            'description': row['Description'],
        })

    return rules_by_field


# ----------------------------------------------------------------------
# Calcul des coefficients tarifaires
# ----------------------------------------------------------------------

def _coefficient_for_age(age: float, rules: list[dict]) -> float:
    """
    Age a deux familles de règles : '<' (jeunes conducteurs, bandes exclusives)
    et '>=' (seniors, on prend le seuil le plus spécifique atteint).
    """
    young_rules = sorted(
        (r for r in rules if r['operator'] == '<'),
        key=lambda r: float(r['value'])
    )
    for r in young_rules:
        if age < float(r['value']):
            return r['coefficient']

    senior_rules = [r for r in rules if r['operator'] == '>=' and age >= float(r['value'])]
    if senior_rules:
        best = max(senior_rules, key=lambda r: float(r['value']))
        return best['coefficient']

    return 1.0  # conducteur "standard", ni jeune ni senior


def _coefficient_threshold(value: float, rules: list[dict], pick: str = 'max') -> float:
    """
    Pour les champs numériques à seuils cumulatifs (Kilometrage>X, AncienneteClient>=X,
    PuissanceCV>=X) : on prend le seuil le plus spécifique satisfait.
    """
    satisfied = []
    for r in rules:
        threshold = float(r['value'])
        if r['operator'] in ('>', '>=') and (
            (r['operator'] == '>' and value > threshold) or
            (r['operator'] == '>=' and value >= threshold)
        ):
            satisfied.append(r)

    if not satisfied:
        return 1.0

    best = max(satisfied, key=lambda r: float(r['value'])) if pick == 'max' else min(
        satisfied, key=lambda r: float(r['value'])
    )
    return best['coefficient']


def _coefficient_nearest_numeric(value: float, rules: list[dict]) -> float:
    """Pour BonusMalus/NombreSinistres5Ans : valeur numérique, on prend le match le plus proche."""
    numeric_rules = [(float(r['value']), r['coefficient']) for r in rules]
    closest = min(numeric_rules, key=lambda pair: abs(pair[0] - value))
    return closest[1]


def _coefficient_exact_match(value: str, rules: list[dict]) -> float:
    """Pour les champs catégoriels (Marque, Ville, Profession, Usage, Categorie, Carburant, GarageFerme)."""
    for r in rules:
        if r['value'].strip().lower() == str(value).strip().lower():
            return r['coefficient']
    return 1.0  # valeur inconnue -> pas de surcharge/décote


def compute_price_coefficient(profile: dict[str, Any], rules_by_field: dict[str, list[dict]]) -> tuple[float, dict]:
    """
    Calcule le coefficient tarifaire total pour un profil client, en combinant
    tous les facteurs disponibles dans le profil. Retourne (coefficient_total, détail par facteur).
    """
    breakdown = {}
    total = 1.0

    def apply(field: str, coeff: float):
        nonlocal total
        breakdown[field] = round(coeff, 4)
        total *= coeff

    if 'Age' in profile and 'Age' in rules_by_field:
        apply('Age', _coefficient_for_age(float(profile['Age']), rules_by_field['Age']))

    if 'BonusMalus' in profile and 'BonusMalus' in rules_by_field:
        apply('BonusMalus', _coefficient_nearest_numeric(float(profile['BonusMalus']), rules_by_field['BonusMalus']))

    if 'NombreSinistres5Ans' in profile and 'Historique' in rules_by_field:
        apply('NombreSinistres5Ans', _coefficient_nearest_numeric(float(profile['NombreSinistres5Ans']), rules_by_field['Historique']))

    if 'Kilometrage' in profile and 'Kilometrage' in rules_by_field:
        apply('Kilometrage', _coefficient_threshold(float(profile['Kilometrage']), rules_by_field['Kilometrage']))

    if 'AncienneteClient' in profile and 'Fidelite' in rules_by_field:
        apply('AncienneteClient', _coefficient_threshold(float(profile['AncienneteClient']), rules_by_field['Fidelite']))

    if 'PuissanceCV' in profile and 'Puissance' in rules_by_field:
        apply('PuissanceCV', _coefficient_threshold(float(profile['PuissanceCV']), rules_by_field['Puissance']))

    for field, category in [
        ('Marque', 'Marque'), ('Ville', 'Zone'), ('Profession', 'Profession'),
        ('Usage', 'Usage'), ('Categorie', 'Vehicule'), ('Carburant', 'Vehicule'),
        ('GarageFerme', 'Stationnement'),
    ]:
        if field in profile and category in rules_by_field:
            apply(field, _coefficient_exact_match(profile[field], rules_by_field[category]))

    return total, breakdown


# ----------------------------------------------------------------------
# Recommandation de packs
# ----------------------------------------------------------------------

def recommend_packs(
    profile: dict[str, Any],
    packs: list[dict],
    eligibility: dict[str, dict],
    rules_by_field: dict[str, list[dict]],
    budget: Optional[float] = None,
    top_n: int = 3,
) -> list[dict]:
    """
    Calcule un classement de packs adaptés au profil client.

    Args:
        profile: dict avec les champs du client (Age, Ville, Profession, Usage,
                 Kilometrage, GarageFerme, Marque, Categorie, Carburant, BonusMalus,
                 NombreSinistres5Ans, AncienneteClient, PuissanceCV). Tous optionnels
                 sauf Usage et Kilometrage, nécessaires au filtrage d'éligibilité.
        packs: résultat de load_packs()
        eligibility: résultat de load_eligibility()
        rules_by_field: résultat de load_rules()
        budget: budget annuel déclaré par le client (optionnel)
        top_n: nombre de packs à retourner

    Returns:
        Liste de dicts triés par pertinence décroissante, avec le détail du calcul.
    """
    coefficient, breakdown = compute_price_coefficient(profile, rules_by_field)

    client_usage = profile.get('Usage')
    client_km = float(profile.get('Kilometrage', 0))
    client_age = float(profile.get('Age', 30))

    candidates = []
    for pack in packs:
        elig = eligibility.get(pack['PackID'], {})
        estimated_price = round(pack['PrixBase'] * coefficient, 2)

        # Règles d'exclusion dures : usage non couvert, kilométrage dépassant la limite,
        # âge du conducteur sous le minimum requis pour ce pack.
        usage_ok = (client_usage in elig.get('UsageRecommande', [])) if client_usage else True
        km_ok = client_km <= pack['LimiteKilometrique']
        age_ok = client_age >= elig.get('AgeMinConducteur', 18)

        eligible = usage_ok and km_ok and age_ok

        # Score de pertinence : complétude de couverture + proximité au budget
        coverage_score = (pack['_coverage_count'] / 12) * 100
        if budget:
            budget_penalty = max(0.0, (estimated_price - budget) / budget) * 100
        else:
            budget_penalty = 0.0

        fit_score = coverage_score - budget_penalty
        if not eligible:
            fit_score -= 1000  # relégué en fin de classement, jamais recommandé en priorité

        candidates.append({
            'PackID': pack['PackID'],
            'Nom': pack['Nom'],
            'Segment': elig.get('Segment', ''),
            'PrixBase': pack['PrixBase'],
            'EstimatedPrice': estimated_price,
            'CoverageCount': pack['_coverage_count'],
            'GarantiesIncluses': pack['_garanties_incluses'],
            'LimiteKilometrique': pack['LimiteKilometrique'],
            'Franchise': pack['Franchise'],
            'Eligible': eligible,
            'EligibilityReasons': {
                'usage_ok': usage_ok, 'kilometrage_ok': km_ok, 'age_ok': age_ok
            },
            'FitScore': round(fit_score, 2),
            'CoefficientDetail': breakdown,
            'Description': pack.get('Description', ''),
        })

    candidates.sort(key=lambda c: c['FitScore'], reverse=True)
    return candidates[:top_n]


# ----------------------------------------------------------------------
# Point d'entrée / exemple d'usage
# ----------------------------------------------------------------------

if __name__ == '__main__':
    base_dir = Path(__file__).parent

    packs = load_packs(str(base_dir / 'packs.csv'))
    eligibility = load_eligibility(str(base_dir / 'pack_eligibility.csv'))
    rules_by_field = load_rules(str(base_dir / 'pricing_rules.csv'))

    # Exemple de profil client rempli via le formulaire
    example_profile = {
        'Age': 29,
        'Ville': 'Casablanca',
        'Profession': 'Ingénieur',
        'Usage': 'Privé-Travail',
        'Kilometrage': 18000,
        'GarageFerme': 'True',
        'Marque': 'Volkswagen',
        'Categorie': 'Compacte',
        'Carburant': 'Essence',
        'BonusMalus': 0.9,
        'NombreSinistres5Ans': 0,
        'AncienneteClient': 2,
        'PuissanceCV': 6,
    }

    results = recommend_packs(example_profile, packs, eligibility, rules_by_field, budget=6500, top_n=3)

    for i, r in enumerate(results, 1):
        print(f"\n#{i} {r['Nom']} ({r['Segment']}) — {r['EstimatedPrice']} MAD/an")
        print(f"    Score: {r['FitScore']} | Couverture: {r['CoverageCount']}/12 | Éligible: {r['Eligible']}")