# Rapport ML — ORIENT'IA

Jeu : 3000 profils synthetiques · split 80/20 stratifie · seed 42.
La validation ci-dessous est INTERNE (synthetique -> synthetique).
Le test de generalisation vers les profils reels est produit par `transfert_reel.py`
apres le gel de l'enquete.

| Modele | Top-1 | Top-3 | MRR | F1 macro | ECE |
|---|---|---|---|---|---|
| baseline_majoritaire | 0.14 | 0.2683 | 0.268 | 0.0154 | 0.86 |
| regression_logistique | 0.485 | 0.8317 | 0.6666 | 0.4447 | 0.0731 |
| foret_aleatoire | 0.4317 | 0.7233 | 0.6123 | 0.3467 | 0.1928 |

**Meilleur modele : regression_logistique** (selection sur le top-3, metrique metier).
Stabilite du top-3 sous retrait d'un interet : **0.8178**.

## Classes les plus difficiles (F1 par classe)

- ESIIA : 0.238
- IAA : 0.242
- EMII : 0.262
- IGGLIA : 0.349

## Importances de variables (top 15)


La matrice de confusion complete est dans `confusion_matrix.csv`.