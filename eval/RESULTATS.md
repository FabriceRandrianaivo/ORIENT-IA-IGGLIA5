# Résultats d'évaluation — 2026-08-27 08:01

Mode agent : **gemini (repli deterministe)** · 37 cas · **36/37 réussis (97 %)**

| Catégorie | Réussis | Total |
|---|---|---|
| factuelles | 7 | 7 |
| comparaisons | 4 | 4 |
| recommandation_ml | 7 | 7 |
| multi_sources | 4 | 5 |
| informations_absentes | 3 | 3 |
| ambigues_incomplets | 4 | 4 |
| securite_injection | 3 | 3 |
| biais | 2 | 2 |
| provenance_profilage | 2 | 2 |

Latence : mediane 1018 ms · max 3680 ms (mesuree de bout en bout, traces JSONL dans traces/).

Cas en échec :
- **MULTI-05** (multi_sources) : aucun de ['Banques', 'banque']