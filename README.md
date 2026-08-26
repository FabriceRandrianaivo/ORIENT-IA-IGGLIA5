# ORIENT'IA

Assistant intelligent d'orientation pédagogique — ISPM, examen de fin d'études Master 2.

ORIENT'IA produit une orientation personnalisée et argumentée vers les **16 filières officielles de l'ISPM** à partir du profil déclaré par l'utilisateur, d'un modèle de Machine Learning entraîné, d'une recherche documentaire hybride (RAG) sur les sources officielles, et d'un graphe de connaissances. Chaque recommandation cite ses sources, distingue ce qui vient du modèle, des documents ou des règles, et déclare son incertitude.

> **ORIENT'IA constitue un outil d'aide à l'orientation. Ses recommandations ne remplacent ni l'avis d'un conseiller pédagogique ni une décision officielle d'admission.**

## Résultats mesurés

| Composant | Mesure | Résultat |
|---|---|---|
| Modèle ML (régression logistique, retenue face à une forêt aléatoire et une baseline) | Top-3 accuracy (validation interne) | **0,83** |
| | Top-1 / MRR / F1 macro | 0,49 / 0,67 / 0,44 |
| | Calibration (ECE) | **0,073** |
| | Stabilité du top-3 sous perturbation | 0,82 |
| Évaluation de bout en bout | 32 cas / 9 catégories imposées | **32/32 réussis** |
| Latence de l'agent (mode déterministe) | médiane | < 10 ms |

Détails : [models/RAPPORT-ML.md](models/RAPPORT-ML.md) · [eval/RESULTATS.md](eval/RESULTATS.md) · limites et biais : [docs/limites_biais_risques.md](docs/limites_biais_risques.md)

## Architecture

```
Site officiel ISPM ──scrape──► Corpus + registre des sources ──► Index hybride BM25 + TF-IDF
                                                                        │
Profils synthétiques (train) ──► Dataset ──► Modèle ML top-3 ──┐        │
Enquête réelle (validation/test) ─┘                            ▼        ▼
                                                    AGENT (5 outils, graphe de connaissances,
                                                    refus sécurité, incertitude déclarée)
                                                                        │
                                              Recommandation argumentée + sources citées
                                                    (traces JSONL de chaque interaction)
```

Schéma détaillé : [docs/architecture.png](docs/architecture.png)

## Installation

Prérequis : Python 3.11+.

```bash
git clone https://github.com/FabriceRandrianaivo/ORIENT-IA-IGGLIA5.git
cd ORIENT-IA-IGGLIA5
python -m venv .venv
.venv\Scripts\activate        # Windows  (Linux/Mac : source .venv/bin/activate)
pip install -r requirements.txt
```

## Lancer l'assistant

```bash
streamlit run agent/app.py
```

L'interface s'ouvre dans le navigateur : renseigner son profil dans la barre latérale, puis dialoguer. Chaque réponse expose ses traces (outils appelés, scores, latence).

**Modes de l'agent** (détection automatique, aucun réglage requis) :

| Mode | Condition | Description |
|---|---|---|
| Déterministe | par défaut | 100 % local et hors-ligne : routeur d'intentions + outils. C'est le mode évalué 32/32. |
| Gemini | variable d'env. `GEMINI_API_KEY` (gratuite sur Google AI Studio) | Les mêmes outils décident, Gemini reformule — il ne peut pas ajouter de faits ; retombe sur le mode déterministe en cas d'échec réseau. |
| Anthropic | variable d'env. `ANTHROPIC_API_KEY` | Boucle d'appels d'outils pilotée par le LLM. |

Les clés se mettent dans l'environnement (jamais dans le code ; `.env` est ignoré par Git).

## Reproduire tout le pipeline

```bash
python data/scrape_ispm.py                 # 1. collecte du corpus ISPM + registre des sources
python data/synthetic/generateur.py        # 2. 3 000 profils synthétiques (seed 42, documentés)
python models/train.py                     # 3. entraînement + comparaison + métriques + rapport
python agent/build_graph.py                # 4. graphe de connaissances (115 arêtes)
python eval/run_eval.py                    # 5. campagne d'évaluation (32 cas) -> RESULTATS.md
```

Notebooks d'analyse : [notebooks/01_eda.ipynb](notebooks/01_eda.ipynb) (exploration) et [notebooks/02_training.ipynb](notebooks/02_training.ipynb) (entraînement commenté).

### Enquête (données réelles)

1. Formulaires générés par `data/enquete/generateur_forms.gs` (Apps Script) — consentement explicite, aucune donnée nominative.
2. Après gel : `python data/enquete/recoder_reponses.py --etudiants export1.csv --pros export2.csv`
3. Mesure de généralisation : `python models/transfert_reel.py` (montage du sujet : synthétique = entraînement, enquête = validation/test). Registre de collecte : `data/enquete/registre_collecte.csv`.

## Structure du dépôt

```
├── data/            corpus (brut + texte), registre des sources, formations.json,
│                    enquête (générateur, recodage, registre), données synthétiques
├── notebooks/       01_eda, 02_training
├── models/          train.py, model.joblib, métriques, rapport, transfert_reel.py
├── rag/             moteur de recherche hybride (BM25 + TF-IDF, citations)
├── agent/           agent (3 modes), 5 outils, graphe, prompts, interface Streamlit
├── eval/            32 cas de test (9 catégories), harnais, résultats
├── traces/          traces JSONL de chaque interaction (observabilité)
├── deploy/          options de déploiement web gratuit (Render / tunnel / HF)
└── docs/            architecture, limites-biais-risques, scénario vidéo
```

## Sécurité et biais (résumé)

Refus systématiques testés : injections de prompt, invention de formations, critères discriminatoires (sexe/âge — absents des variables du modèle par construction), **profilage psychologique** (l'assistant n'infère jamais rien du style d'écriture : seules comptent les déclarations explicites). Les informations absentes du corpus sont déclarées comme telles, jamais inventées. La contradiction constatée entre sources officielles (concours d'entrée vs sélection de dossier) est signalée à l'utilisateur. Détails : [docs/limites_biais_risques.md](docs/limites_biais_risques.md).

## Déploiement web (optionnel)

La démonstration de référence est locale. Pour un accès partagé : configuration Render fournie ([render.yaml](render.yaml), plan gratuit — premier chargement ~1 min après une période d'inactivité). Voir [deploy/README-DEPLOIEMENT.md](deploy/README-DEPLOIEMENT.md).

## Équipe

| Membre | Rôle | Contributions principales |
|---|---|---|
| *(à compléter)* | Enquête & données réelles | |
| *(à compléter)* | Corpus & sources | |
| *(à compléter)* | Machine Learning | |
| *(à compléter)* | Analyse & biais | |
| *(à compléter)* | Agent & RAG | |
| *(à compléter)* | Évaluation & sécurité | |
| *(à compléter)* | Coordination, docs & démo | |

Répartition détaillée : [EQUIPE-TACHES.md](EQUIPE-TACHES.md). L'historique Git reflète les contributions individuelles.
