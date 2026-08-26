# ORIENT'IA — Limites, biais et risques

Livrable 12 du sujet. Principe directeur : nommer les limites plutôt que les masquer.

## 1. Limites des données

**Corpus documentaire.** Le corpus provient exclusivement du site officiel de l'ISPM (4 pages + brochure PDF, voir `data/registre_sources.csv`). Conséquences :
- Les **maquettes détaillées** (listes de matières par année, volumes horaires) ne sont pas publiées : `formations.json` marque ces champs `null` et l'assistant répond « information non disponible » — jamais d'invention.
- La **brochure n'est pas datée** (prix listés jusqu'en 2009) : son contenu est potentiellement obsolète, il est cité avec cette réserve.
- **Contradiction entre sources** : la brochure mentionne un « concours d'entrée », la page inscription une « sélection de dossier ». L'assistant signale la contradiction et renvoie vers l'administration.
- Le site mélange deux encodages (UTF-8 / Windows-1252) — corrigé par le script de collecte, documenté ici car c'est une fragilité de la source.

**Données synthétiques** (détail complet : `data/synthetic/DONNEES-SYNTHETIQUES.md`) :
- Générées par des règles d'affinité écrites par l'équipe → un modèle entraîné dessus apprend d'abord ces règles (limite énoncée par le sujet lui-même). Parade : validation sur données réelles d'enquête.
- Déséquilibre de classes (CAA ~14 % → IAA ~1,6 %) : compensé par pondération de classes, mais les classes rares restent moins bien apprises (voir F1 par classe dans `models/metrics.json`).
- Bruit d'étiquette volontaire (tirage softmax) : plafonne le top-1 vers ~0,5 par construction — c'est un choix documenté, pas un défaut caché.

**Enquête réelle** (les trois limites du sujet, assumées) :
- **Volume** : quelques dizaines à centaines de réponses au mieux → intervalles de confiance larges, annoncés comme tels dans `models/transfert_reel.py`.
- **Auto-sélection** : les répondants sur-représentent nos réseaux (promo, filières informatiques probablement) — constaté et chiffré dans le registre de collecte après gel.
- **Nature de l'étiquette** : chez un étudiant, le parcours *choisi* n'est pas forcément celui qui *convenait* ; le jugement rétrospectif des professionnels corrige en partie, au prix d'un biais de reconstruction mémorielle et d'un décalage temporel (l'offre de formation a changé).

## 2. Limites du modèle ML

- Régression logistique : hypothèse de séparabilité linéaire — assumée car elle **bat** la forêt aléatoire en généralisation ET en calibration (ECE 0,073 vs 0,193) sur ce jeu.
- Top-1 ≈ 0,49 : reflète le bruit d'étiquette irréductible ; la métrique métier est le **top-3 (0,83)** car le système propose 3 parcours, jamais un verdict unique.
- La **mesure décisive** — le transfert synthétique → profils réels — dépend de l'enquête ; tant qu'elle n'est pas gelée, les performances rapportées sont internes au synthétique.
- Stabilité : retirer un centre d'intérêt conserve en moyenne 82 % du top-3 — les 18 % restants montrent que le modèle reste sensible aux petites variations de profil.

## 3. Limites de l'agent

- **Mode déterministe** (celui évalué 32/32) : routeur d'intentions à motifs — couvre les formulations testées mais pas toute la variété du français spontané ; une question très inhabituelle retombe sur la recherche documentaire ou l'aveu d'ignorance (comportement sûr par défaut).
- **Détection de sécurité par motifs** (injection, discrimination, profilage) : robuste sur les formulations directes et testée, mais un adversaire créatif peut la contourner — le system prompt LLM constitue la seconde ligne de défense, et aucune variable sensible n'existe de toute façon dans le modèle.
- **Modes LLM** (Gemini/Anthropic, optionnels) : le LLM reformule à partir des sorties d'outils et ne peut pas ajouter de faits (consigne stricte + repli automatique sur le mode déterministe en cas d'échec) ; le risque résiduel de reformulation inexacte existe et est tracé.
- La recherche hybride repose sur du lexical (BM25 + TF-IDF, pluriels repliés) : les synonymes éloignés (« informatique » vs « numérique ») peuvent rater — atténué par les fiches structurées qui couvrent les 16 filières.

## 4. Risques pris en charge (exigence section 16 du sujet)

| Risque | Défense | Preuve |
|---|---|---|
| Injection de prompt | Détection par motifs avant tout traitement + system prompt | SEC-01..03 (32/32) |
| Instructions malveillantes dans les documents | Le contenu documentaire n'est jamais interprété comme instruction (outils = données JSON) | conception + SEC-01 |
| Questions hors sujet | Recherche → si non couvert : « information non disponible » + renvoi contact officiel | ABS-01..03 |
| Demandes d'informations personnelles | Aucune donnée personnelle stockée ; profil déclaré, local à la session | conception |
| Informations contradictoires | Contradiction concours/dossier documentée et signalée | `formations.json`, FACT-05 |
| Critères discriminatoires | Sexe/âge absents des variables du modèle par construction + refus explicite | BIAIS-01..02 |
| Profilage psychologique | Refus systématique ; seules les déclarations explicites comptent | PROV-02 |
| Affirmations non justifiées | Citations [src-…] obligatoires, distinction ML/documents/règles | toutes catégories |
| Conseil ≠ décision administrative | Mention obligatoire affichée en permanence + renvoi administration | interface + MULTI-01 |

## 5. Risques résiduels

- Obsolescence du corpus si le site ISPM évolue (le scraper permet une re-collecte en une commande ; le registre horodate chaque consultation).
- Sur-confiance de l'utilisateur malgré la mention obligatoire — atténuée par l'affichage systématique des probabilités et des avertissements dans chaque recommandation.
- Représentativité de l'enquête non garantie — chiffrée et publiée plutôt que corrigée artificiellement.
