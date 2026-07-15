## accident_statistics.csv

Colonnes: StatisticID,Annee,Ville,Region,Accidents,Blesses,Deces,TauxGravite

AS00001,2020,Casablanca,Grand Casablanca,1474,441,41,0.057
AS00002,2021,Casablanca,Grand Casablanca,2274,699,67,0.079
AS00003,2022,Casablanca,Grand Casablanca,3058,1093,41,0.092
AS00004,2023,Casablanca,Grand Casablanca,1311,359,34,0.09

## cities.csv

Colonnes: CityID,Ville,CodePostal,Region,CoefficientZone,Population,TauxSinistralite,IndiceVol

C001,Casablanca,20000,Grand Casablanca,1.28,2781950,0.1124,1.3
C002,Rabat,10000,Rabat-Salé-Kénitra,1.18,1127150,0.1128,1.2
C003,Marrakech,40000,Marrakech-Safi,1.22,2938283,0.1609,1.08
C004,Fès,30000,Fès-Meknès,1.15,2576705,0.126,0.6

## clients.csv

Colonnes: ClientID,Nom,Prenom,Sexe,Age,DateNaissance,Ville,CodePostal,Profession,SituationFamiliale,NombreEnfants,SalaireMensuel,Email,Telephone,DateInscription,AncienneteClient,ScoreFidelite,AnciennetePermis,TypePermis,BonusMalus,NombreSinistres5Ans,KilometrageAnnuel,GarageFerme,UsageVehicule,RiskScore

CL000001,El Amrani,Amina,F,46,1980-05-25,Beni Mellal,23000,Étudiant,Pacsé(e),1,1953,sophie.elamrani1@outlook.ma,+2120500000001,2013-07-04,12,67.8,7,B,1.04,1,45000,False,Privé,75.9
CL000002,Mernissi,Fatima,F,36,1990-09-05,Fès,30000,Cadre supérieur,Marié(e),2,12663,fatima.mernissi2@outlook.ma,+2120700000002,2016-11-01,9,63.1,6,B,0.82,0,12000,True,Privé,50.9
CL000003,Idrissi,Imane,F,50,1976-03-22,Errachidia,52000,Cadre supérieur,Pacsé(e),0,23327,imane.idrissi3@yahoo.fr,+2120500000003,2024-06-17,1,6.3,17,B,0.75,1,45000,True,Privé-Travail,69.2
CL000004,Ouazzani,Zineb,F,62,1964-03-22,Oujda,60000,Avocat,Veuf(ve),3,17991,zineb.ouazzani4@yahoo.fr,+2120500000004,2017-02-16,8,53.2,0,B,1.0,0,18000,False,Privé,53.9

## conseils.csv

Colonnes: ConseilID,Titre,Categorie,Contenu,Public

CO00001,Déclarez tous les conducteurs habituels du véhicule,Administratif,Déclarez tous les conducteurs habituels du véhicule. Ce conseil est validé par nos experts underwriting.,Jeunes conducteurs
CO00002,Installez un antivol agréé pour réduire le risque vol,Sinistre,Installez un antivol agréé pour réduire le risque vol. Ce conseil est validé par nos experts underwriting.,Professionnels
CO00003,Garez votre véhicule en garage fermé si possible,Administratif,Garez votre véhicule en garage fermé si possible. Ce conseil est validé par nos experts underwriting.,Jeunes conducteurs
CO00004,Mettez à jour votre kilométrage annuel chaque année,Souscription,Mettez à jour votre kilométrage annuel chaque année. Ce conseil est validé par nos experts underwriting.,Jeunes conducteurs

## contracts.csv

Colonnes: ContractID,ClientID,VehicleID,Pack,DateSouscription,DateExpiration,PrimeAnnuelle,PrimeMensuelle,Statut,Franchise,Paiement,Reduction,Taxes,MontantFinal

CT000001,CL000001,VH000001,Business,2025-05-17,2026-05-17,30968.78,2580.73,Résilié,600,Trimestriel,3576.89,3834.86,31226.75
CT000002,CL000001,VH000001,VIP,2024-04-17,2025-04-17,40093.51,3341.13,Actif,500,Trimestriel,4630.8,4964.78,40427.49
CT000003,CL000001,VH000001,Eco+,2019-02-19,2020-02-19,8848.22,737.35,Expiré,2500,Semestriel,1021.97,1095.67,8921.92
CT000004,CL000002,VH000002,Silver,2022-01-25,2023-01-25,5168.85,430.74,Résilié,1800,Trimestriel,498.79,653.81,5323.87

## coverage.csv

Colonnes: CoverageID,Pack,Garantie,Incluse,Niveau

COV0001,Eco,ResponsabiliteCivile,False,Non inclus
COV0002,Eco,Vol,False,Non inclus
COV0003,Eco,Incendie,False,Non inclus
COV0004,Eco,BrisDeGlace,False,Non inclus

## exclusions.csv

Colonnes: ExclusionID,Nom,Categorie,Description,PackImpacte

EX00001,Usage du véhicule en compétition ou sur circuit,Conduite,Usage du véhicule en compétition ou sur circuit. Voir article 5 des CG.,Eco
EX00002,Dommages survenus hors territoire marocain non couvert,Conduite,Dommages survenus hors territoire marocain non couvert. Voir article 1 des CG.,Tous
EX00003,Usure normale et défaut d'entretien,Territorial,Usure normale et défaut d'entretien. Voir article 14 des CG.,VIP
EX00004,Conduite par une personne non déclarée au contrat,Conduite,Conduite par une personne non déclarée au contrat. Voir article 2 des CG.,Silver

## experts.csv

Colonnes: ExpertID,Nom,Prenom,Ville,Specialite,Tier,Note

EXP0001,Riou,Frédéric,Fès,Carrosserie,3,3.9
EXP0002,Laurent,Nicole,Tanger,Carrosserie,5,3.6
EXP0003,Paris,Patrick,El Jadida,Carrosserie,1,3.6
EXP0004,Hubert,Guillaume,Oujda,Corporel,5,3.5

## faq.csv

Colonnes: FAQID,Question,Categorie,Reponse,Tags,Priorite

FAQ00001,Quel est le délai de déclaration d'un sinistre ?,Délais,Vous disposez de 5 jours ouvrés pour déclarer un sinistre, 2 jours en cas de vol. Réf. FAQ-00001.,Délais,assurance auto,Maroc,4
FAQ00002,Comment fonctionne le bonus-malus ?,Bonus Malus,Chaque année sans sinistre responsable réduit votre coefficient de 5%, jusqu'à 0.50 minimum. Réf. FAQ-00002.,Bonus Malus,assurance auto,Maroc,1
FAQ00003,Puis-je assurer une voiture neuve ?,Souscription,Oui, nous proposons des formules véhicule neuf avec valeur à neuf garantie 12 mois. Réf. FAQ-00003.,Souscription,assurance auto,Maroc,2
FAQ00004,Quelle franchise choisir ?,Franchise,Une franchise élevée réduit la prime annuelle mais augmente votre reste à charge en cas de sinistre. Réf. FAQ-00004.,Franchise,assurance auto,Maroc,3

## garages.csv

Colonnes: GarageID,Nom,Ville,CodePostal,AgreeAssureur,Specialite,Note

G0001,Garage Atlas Kénitra,Kénitra,14000,True,Premium,3.3
G0002,Garage Auto Mohammedia,Mohammedia,28800,True,Carrosserie,4.7
G0003,Garage Maghreb Rabat,Rabat,10000,True,Carrosserie,3.8
G0004,Garage Maghreb Marrakech,Marrakech,40000,True,Premium,4.3

## garanties.csv

Colonnes: GarantieID,Nom,Pack,Plafond,Franchise,Description,Active

GA00001,Dommages corporels du conducteur jusqu'à 500 000 MAD,VIP,200000,2000,Dommages corporels du conducteur jusqu'à 500 000 MAD. Applicable selon conditions générales CG-2026.,True
GA00002,Bris de glace sans franchise limité à 2 sinistres/an,Eco,500000,2000,Bris de glace sans franchise limité à 2 sinistres/an. Applicable selon conditions générales CG-2026.,True
GA00003,Assistance 0 km 24h/24 au Maroc et en Europe,Bronze,999999,3000,Assistance 0 km 24h/24 au Maroc et en Europe. Applicable selon conditions générales CG-2026.,True
GA00004,Véhicule de remplacement 7 jours en cas d'accident,Silver+,500000,1000,Véhicule de remplacement 7 jours en cas d'accident. Applicable selon conditions générales CG-2026.,True

## packs.csv

Colonnes: PackID,Nom,PrixBase,ResponsabiliteCivile,Vol,Incendie,BrisDeGlace,CatastrophesNaturelles,DommagesCollision,TousRisques,Assistance,Remorquage,VehiculeRemplacement,ProtectionConducteur,ProtectionJuridique,LimiteKilometrique,Franchise,Description

PK01,Eco,2800,0,0,0,0,0,0,0,1,0,0,0,0,50000,3000,Pack Eco - formule adaptée au profil économique.
PK02,Eco+,3200,1,0,0,1,0,0,0,1,1,0,0,0,80000,2500,Pack Eco+ - formule adaptée au profil standard.
PK03,Bronze,4500,1,0,1,1,0,0,0,1,1,0,0,0,100000,2000,Pack Bronze - formule adaptée au profil confort.
PK04,Silver,5800,1,1,1,1,0,1,0,1,1,0,1,0,120000,1800,Pack Silver - formule adaptée au profil premium.

## pricing_rules.csv

Colonnes: RuleID,Condition,Coefficient,Description,Categorie

R0001,Age<21,1.45,Jeune conducteur 18-20 ans,Age
R0002,Age<24,1.39,Jeune conducteur 21-23 ans,Age
R0003,Age<27,1.33,Jeune conducteur 24-26 ans,Age
R0004,Age>=66,1.07,Conducteur senior 66+ ans,Age

## professions.csv

Colonnes: ProfessionID,Profession,Categorie,SalaireMoyen,CoefficientRisque

P001,Employé de bureau,Salarié,6500,1.0
P002,Cadre supérieur,Salarié,18000,0.92
P003,Médecin,Profession libérale,22000,0.88
P004,Avocat,Profession libérale,20000,0.9

## recommendations.csv

Colonnes: ClientID,Pack1,Score1,Pack2,Score2,Pack3,Score3,PrixEstime,Justification

CL000001,Gold,54.0,Gold+,53.9,Business,53.6,21747.2,Le conducteur roule beaucoup. Le pack Gold est recommandé en priorité.
CL000002,Premium,67.1,Silver+,66.7,Bronze,66.5,8995.49,Le bonus est excellent. Le stationnement en garage fermé réduit le risque vol. Le pack Premium est recommandé en priorité.
CL000003,Business,86.5,Gold,85.9,Premium,85.9,20076.53,Le conducteur roule beaucoup. Le bonus est excellent. L'usage professionnel requiert des garanties adaptées. Le stationnement en garage fermé réduit le risque vol. Le pack Business est recommandé en priorité.
CL000004,Eco,68.0,Bronze,67.4,Business,66.5,2975.13,Le pack Eco est recommandé en priorité.

## vehicules.csv

Colonnes: VehicleID,ClientID,Marque,Modele,Version,Annee,Categorie,Carburant,Transmission,PuissanceDIN,PuissanceCV,ValeurNeuve,ValeurActuelle,NombrePlaces,Poids,Cylindree,Couleur,NombrePortes,VIN,Immatriculation,Etat

VH000001,CL000001,Ford,Fiesta,Fiesta Iconic,2017,Citadine,Hybride,Manuelle,85,5,218400,125142.06,5,1080,998,Blanc,5,WF0E92278879CBE83,79849|BN|6,Usé
VH000002,CL000002,Volkswagen,Polo,Polo Iconic,2022,Citadine,Diesel,Manuelle,95,5,225000,161188.42,5,1100,999,Vert,5,WVW846FAAEAFAEE1E,23562|YS|4,Bon
VH000003,CL000003,Volkswagen,Golf,Golf Active,2013,Compacte,Essence,Manuelle,110,6,315000,140920.01,5,1280,999,Beige,5,WVW6944D4FB5E8BAA,00003-C-7,Usé
VH000004,CL000004,Ford,Fiesta,Fiesta Intens,2014,Citadine,Hybride,Manuelle,85,5,218400,103941.0,5,1080,998,Blanc,5,WF0DC3EE8DAB7C1FE,99999|WX|1,Correct
