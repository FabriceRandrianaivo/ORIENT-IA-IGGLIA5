# ORIENT'IA

Assistant intelligent d'orientation pédagogique — ISPM, examen de fin d'études Master 2.

ORIENT'IA produit une orientation personnalisée et argumentée à partir du profil déclaré par l'utilisateur, des informations officielles sur les formations de l'ISPM, d'un modèle de Machine Learning et d'une recherche documentaire (RAG). Chaque recommandation cite ses sources et déclare son incertitude.

> ORIENT'IA constitue un outil d'aide à l'orientation. Ses recommandations ne remplacent ni l'avis d'un conseiller pédagogique ni une décision officielle d'admission.

## Structure du dépôt

```
├── data/            Corpus pédagogique, registre des sources, enquête, données synthétiques
├── notebooks/       Analyse exploratoire et entraînement
├── models/          Modèle entraîné et script de reproduction
├── rag/             Ingestion, index et recherche documentaire
├── agent/           Agent conversationnel, outils et interface
├── eval/            Jeu d'évaluation (32+ cas) et résultats
├── traces/          Traces d'exécution (JSONL)
└── docs/            Architecture, note limites/biais/risques, vidéo
```

## Installation

*(à compléter — instructions testées sur machine vierge avant la remise)*

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Exécution

*(à compléter)*

## Équipe

*(à compléter — un membre par ligne, avec son rôle)*
