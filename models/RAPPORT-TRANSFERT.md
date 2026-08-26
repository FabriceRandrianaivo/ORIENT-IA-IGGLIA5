# Transfert synthétique → réel — la mesure de généralisation

Montage recommandé par le sujet : **entraînement sur données synthétiques, test sur les
réponses d'enquête réelles**. Mesure produite par `models/transfert_reel.py` le 26/08/2026
sur l'export gelé de l'enquête (fichier `data/enquete/export_reponses.csv`, 98 réponses
reçues → 79 retenues après recodage, motifs d'écartement dans `reponses_ecartees.csv`).

## Résultats

| Population | n | Top-1 | Top-3 | MRR | F1 macro | ECE |
|---|---|---|---|---|---|---|
| **Toutes** | **79** | **0,481** | **0,734 ± 0,10** | 0,634 | 0,403 | 0,114 |
| Étudiants | 71 | 0,451 | 0,718 | 0,610 | 0,357 | 0,130 |
| Professionnels | 8 | 0,750 | 0,875 | 0,844 | 0,524 | 0,188 |
| *Référence : validation interne (synthétique)* | *600* | *0,485* | *0,832* | *0,667* | *0,445* | *0,073* |

Intervalle de confiance à 95 % sur le top-3 global : **± 10 points** (n = 79).

## Lecture

- **Le modèle généralise réellement** : la perte de transfert sur la métrique métier
  (top-3) est limitée à **~10 points** (0,83 → 0,73), et le top-1 est quasi identique
  (0,485 synthétique vs 0,481 réel). Les règles d'affinité encodées dans le générateur
  capturent donc une vraie structure des choix d'orientation, pas seulement leurs
  propres artefacts.
- **Les professionnels** (population que le sujet juge la plus précieuse) obtiennent le
  meilleur score (0,875 top-3) — mais n = 8 : à citer avec l'intervalle très large qui
  s'impose, comme le sujet l'exige.
- **La calibration se dégrade modérément** (ECE 0,073 → 0,114) : les probabilités
  restent utilisables pour exprimer l'incertitude, avec cette réserve déclarée.

## Limites de la mesure (à annoncer, cf. sujet)

- **Auto-sélection** : 15 filières sur 16 représentées (ICMP absente), mais IGGLIA
  sur-représentée (20/79, ~25 % — réseau de l'équipe) ; séries D majoritaires (43/79).
- **Volume** : 79 réponses → IC ± 10 points ; les scores par population (surtout pros,
  n = 8) sont indicatifs.
- **Nature de l'étiquette** : chez les étudiants, le parcours *choisi* n'est pas
  forcément celui qui *convenait* (le jugement rétrospectif des 8 professionnels
  corrige partiellement, au prix d'un biais de reconstruction).
- 19 réponses écartées de façon documentée : 7 « autre établissement » sans filière
  précisée, 12 filières professionnelles trop génériques pour être rattachées sans
  deviner (ex. « Informatique » seul, ambigu entre 4 parcours ISPM).

Reproduire : `python models/transfert_reel.py [--population etudiant|professionnel]`
