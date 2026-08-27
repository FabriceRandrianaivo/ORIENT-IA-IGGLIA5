# Répartition des tâches — équipe de 7

Chacun commite **avec son propre compte GitHub** sur la branche indiquée (le jury lit l'historique).
Attribution en cohérence avec le tableau Équipe du README.

| # | Rôle | Branche | Tâches (dans l'ordre) |
|---|------|---------|------------------------|
| **M1** — [@AndrianandrasanaFy](https://github.com/AndrianandrasanaFy) | Enquête & données réelles | `phase1-donnees` | 1. Créer les 2 Google Forms (ENQUETE-QUESTIONNAIRES.md) **MAINTENANT**, sans collecte d'e-mails. 2. Diffuser (promos, anciens, LinkedIn, famille) et relancer dans la journée. 3. Tenir `data/enquete/registre_collecte.csv` au fil de l'eau. 4. Ce soir : geler, exporter, anonymiser. 5. Recoder au format de `data/synthetic/dataset.csv` → `reponses_recodees.csv`. |
| **M2** — [@AinaAnjaratiana](https://github.com/AinaAnjaratiana) & Liantsoa Nombana ([@nombanaANDRIANJOHANY](https://github.com/nombanaANDRIANJOHANY)) | Corpus & sources | `phase1-donnees` | 1. Relire `data/formations.json` et le registre. 2. Chercher des sources complémentaires licites (brochures papier, maquettes, groupes officiels) et les ajouter au corpus + registre. 3. Préparer `docs/limites_biais_risques.md` (premier jet depuis DONNEES-SYNTHETIQUES.md et le registre). |
| **M3** — [@ninih-sama](https://github.com/ninih-sama) | ML lead | `phase2-ml` | 1. Relire/exécuter `models/train.py` et les notebooks 01–02. 2. Affiner si utile (hyperparamètres, 3e modèle). 3. Dès que M1 livre `reponses_recodees.csv` → `python models/transfert_reel.py` et commenter les résultats. 4. Analyse d'erreurs écrite (quelles filières se confondent, pourquoi). |
| **M4** — [@mampiona](https://github.com/mampiona) | Analyse & biais ML | `phase2-ml` | 1. Exécuter et enrichir `01_eda.ipynb` (figures propres). 2. Rédiger l'étude biais/limites ML (classes rares, bruit d'étiquette, auto-sélection de l'enquête). 3. Vérifier la stabilité et la calibration, produire les graphiques pour le rapport. |
| **M5** — **Fabrice Randrianaivo** ([@FabriceRandrianaivo](https://github.com/FabriceRandrianaivo)) | Agent & RAG lead | `phase3-agent` | 1. `rag/` : ingestion + recherche sur le corpus. 2. `agent/tools.py` : les 5 outils. 3. Boucle agent + LLM + system prompt (refus, incertitude, renvoi administration). 4. Interface Streamlit avec mention obligatoire + panneau traces. |
| **M6** — [@nyanjaraandria](https://github.com/nyanjaraandria) | Évaluation & sécurité | `phase4-eval` | 1. Rédiger les 32+ cas dans `eval/eval_cases.jsonl` (9 catégories du sujet) — **commencer tout de suite, ne dépend pas du code**. 2. Écrire `eval/run_eval.py` (harnais de rejeu). 3. Demain : campagne complète, corrections sécurité en priorité, figer `eval_results.csv`. |
| **M7** — Fabrice Randrianaivo (coordination) & [@nyanjaraandria](https://github.com/nyanjaraandria) (vidéo) | Coordination, docs & démo | `develop` | 1. Gérer les merges phase → develop (+ résoudre les conflits). 2. README final + schéma d'architecture (`docs/`). 3. Préparer le scénario vidéo 3–5 min et la tournage demain après-midi. 4. Répéter les 9 questions du jury (PLAN-ORIENTIA.md §14) avec toute l'équipe. 5. Tenir SUIVI.html à jour. |

## Règles de collaboration

- **Petits commits fréquents**, messages clairs en français, chacun sur sa branche de phase.
- Merge vers `develop` uniquement via M7 (ou après accord rapide à deux).
- Personne ne touche `main` avant la remise finale.
- Blocage > 30 min → on le dit dans le groupe, on ne reste pas coincé seul.
- Toute info ajoutée au corpus passe par le registre des sources — **jamais d'info non sourcée**.

## Jalons du jour (aujourd'hui, mercredi 26)

1. **Avant midi** : enquête lancée (M1) · cas de test commencés (M6) · agent squelette (M5).
2. **Fin d'après-midi** : ML validé (M3/M4) · 3 outils fonctionnels (M5) · ≥ 20 cas rédigés (M6).
3. **Ce soir** : enquête gelée + recodée (M1) · transfert réel mesuré (M3) · agent complet avec traces (M5).

Demain (jeudi 27) : campagne d'évaluation, corrections, docs, vidéo — **remise visée 16 h 00**.
