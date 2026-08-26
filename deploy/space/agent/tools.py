"""Les outils de l'agent ORIENT'IA (exigence du sujet : >= 3 outils fonctionnels).

Chaque outil est une vraie fonction Python avec entrees/sorties JSON-serialisables :
    rechercher_formation(question)            recherche hybride dans le corpus
    analyser_profil_ml(profil)                top-3 du modele entraine + facteurs
    verifier_prerequis(serie_bac, sigle, ...) regles officielles + graphe
    comparer_parcours(sigle1, sigle2)         comparaison structuree sourcee
    calculer_score_adequation(profil, sigle)  score ML x prerequis, explique

Le sexe et l'age ne font partie d'aucune entree : ils ne peuvent pas etre
utilises comme criteres (exigence securite du sujet).
"""

import json
import sys
from pathlib import Path

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "models"))
sys.path.insert(0, str(ROOT / "rag"))

from moteur import Recherche          # noqa: E402
from train import align, build_features  # noqa: E402

# --------------------------------------------------------------- chargements
_FORMATIONS = json.loads((ROOT / "data" / "formations.json").read_text(encoding="utf-8"))
_PAR_SIGLE = {f["sigle"]: f for f in _FORMATIONS["filieres"]}
_BUNDLE = joblib.load(ROOT / "models" / "model.joblib")
_GRAPHE = json.loads((ROOT / "agent" / "graph.json").read_text(encoding="utf-8"))
_RECHERCHE = Recherche()

# Vocabulaire attendu du profil (identique au questionnaire et au dataset).
SERIES = ["A1", "A2", "C", "D", "S", "L", "Technique industrielle",
          "Technique genie civil", "Technique agricole"]
SCIENTIFIQUES = {"C", "D", "S"}
ELIGIBILITE = {
    **{s: SCIENTIFIQUES | {"Technique industrielle"} for s in ["IGGLIA", "ESIIA", "IMTICIA", "ISAIA", "EMII", "ICMP"]},
    "GCA": SCIENTIFIQUES | {"Technique genie civil"},
    **{s: SCIENTIFIQUES | {"Technique agricole", "A2"} for s in ["IAA", "PIP", "AEE"]},
    **{s: set(SERIES) for s in ["CAA", "FIC", "DTJA", "EMP", "TEE", "TEH"]},
}

CHAMPS_PROFIL = ["serie_bac", "note_maths", "note_sciences", "note_langues", "note_eco",
                 "matieres_preferees", "competences", "interets", "environnement", "metiers_vises"]


def _profil_vers_ligne(profil: dict) -> pd.DataFrame:
    ligne = {
        "serie_bac": profil.get("serie_bac", ""),
        "environnement": profil.get("environnement", ""),
        **{n: int(profil.get(n, 3)) for n in ["note_maths", "note_sciences", "note_langues", "note_eco"]},
    }
    for champ in ["matieres_preferees", "competences", "interets", "metiers_vises"]:
        val = profil.get(champ, [])
        ligne[champ] = "|".join(val) if isinstance(val, list) else str(val)
    return pd.DataFrame([ligne])


def champs_manquants(profil: dict) -> list:
    """Champs importants absents -> l'agent doit poser des questions, pas deviner."""
    vides = []
    for champ in ["serie_bac", "matieres_preferees", "interets"]:
        v = profil.get(champ)
        if not v:
            vides.append(champ)
    return vides


# ------------------------------------------------------------------- outil 1
def rechercher_formation(question: str, k: int = 5) -> dict:
    passages = _RECHERCHE.rechercher(question, k)
    return {"passages": passages,
            "note": "Scores hybrides BM25 + TF-IDF ; sources = identifiants du registre data/registre_sources.csv."}


# ------------------------------------------------------------------- outil 2
def analyser_profil_ml(profil: dict) -> dict:
    manquants = champs_manquants(profil)
    if manquants:
        return {"erreur": "profil_incomplet", "champs_manquants": manquants,
                "message": "Informations importantes absentes : demander a l'utilisateur avant de recommander."}
    model, columns = _BUNDLE["model"], _BUNDLE["columns"]
    X = align(build_features(_profil_vers_ligne(profil)), columns)
    proba = model.predict_proba(X)[0]
    ordre = proba.argsort()[::-1][:3]
    top3 = [{"sigle": model.classes_[i], "nom": _PAR_SIGLE[model.classes_[i]]["nom"],
             "probabilite": round(float(proba[i]), 3)} for i in ordre]

    # Facteurs : contributions de la regression logistique pour la 1re classe.
    facteurs = []
    if hasattr(model, "coef_"):
        idx = list(model.classes_).index(top3[0]["sigle"])
        contrib = model.coef_[idx] * X.iloc[0].values
        meilleurs = contrib.argsort()[::-1][:4]
        facteurs = [columns[i] for i in meilleurs if contrib[i] > 0]

    return {"top3": top3, "facteurs_principaux": facteurs,
            "modele": _BUNDLE["nom"], "seed": _BUNDLE["seed"],
            "avertissement": ("Modele entraine sur donnees synthetiques documentees "
                              "(data/synthetic/DONNEES-SYNTHETIQUES.md) ; score = aide a la "
                              "decision, pas un verdict.")}


# ------------------------------------------------------------------- outil 3
def verifier_prerequis(serie_bac: str, sigle: str, note_maths: int = None) -> dict:
    sigle = sigle.upper()
    if sigle not in _PAR_SIGLE:
        return {"erreur": "filiere_inconnue",
                "message": f"'{sigle}' n'est pas une filiere ISPM connue du corpus.",
                "filieres_valides": sorted(_PAR_SIGLE)}
    ok = serie_bac in ELIGIBILITE[sigle]
    detail = ""
    if serie_bac == "A2" and sigle in {"IAA", "PIP", "AEE"}:
        if note_maths is None:
            detail = "Bac A2 : admis en biotechnologie seulement avec note de mathematiques >= 12/20 (a verifier)."
        elif note_maths < 3:
            ok, detail = False, "Bac A2 avec maths < 12/20 : condition officielle non remplie."
        else:
            detail = "Bac A2 avec maths >= 12/20 : condition remplie."
    return {"filiere": sigle, "serie_bac": serie_bac, "eligible": ok, "detail": detail,
            "regle_officielle": _PAR_SIGLE[sigle]["prerequis_bac"],
            "source": "src-inscription",
            "rappel": "Decision d'admission = administration ISPM uniquement (selection de dossier)."}


# ------------------------------------------------------------------- outil 4
def comparer_parcours(sigle1: str, sigle2: str) -> dict:
    s1, s2 = sigle1.upper(), sigle2.upper()
    inconnus = [s for s in (s1, s2) if s not in _PAR_SIGLE]
    if inconnus:
        return {"erreur": "filiere_inconnue", "inconnues": inconnus,
                "filieres_valides": sorted(_PAR_SIGLE)}
    def fiche(s):
        f = _PAR_SIGLE[s]
        return {"sigle": s, "nom": f["nom"], "departement": f["departement"],
                "description": f["description"], "prerequis_bac": f["prerequis_bac"],
                "debouches": f["debouches"], "matieres_principales": f["matieres_principales"],
                "sources": f["sources"]}
    return {"comparaison": [fiche(s1), fiche(s2)],
            "note": "Champs a null = information non publiee par les sources officielles collectees."}


# ------------------------------------------------------------------- outil 5
def calculer_score_adequation(profil: dict, sigle: str) -> dict:
    sigle = sigle.upper()
    if sigle not in _PAR_SIGLE:
        return {"erreur": "filiere_inconnue", "filieres_valides": sorted(_PAR_SIGLE)}
    analyse = analyser_profil_ml(profil)
    if "erreur" in analyse:
        return analyse
    model, columns = _BUNDLE["model"], _BUNDLE["columns"]
    X = align(build_features(_profil_vers_ligne(profil)), columns)
    proba = dict(zip(model.classes_, model.predict_proba(X)[0]))
    prereq = verifier_prerequis(profil.get("serie_bac", ""), sigle, profil.get("note_maths"))
    return {"filiere": sigle, "score_ml": round(float(proba.get(sigle, 0.0)), 3),
            "rang_ml": int(sorted(proba, key=proba.get, reverse=True).index(sigle)) + 1,
            "prerequis": prereq,
            "verdict": ("compatible" if prereq["eligible"] and proba.get(sigle, 0) >= 0.05
                        else "prerequis non remplis" if not prereq["eligible"]
                        else "faible affinite selon le modele"),
            "avertissement": analyse["avertissement"]}


# --------------------------------------------------------- graphe (extension)
def chemins_graphe(sigle: str) -> dict:
    """Relations sortantes d'un parcours dans le graphe de connaissances."""
    sigle = sigle.upper()
    sortantes = [a for a in _GRAPHE["aretes"] if a[0] == sigle]
    return {"parcours": sigle,
            "relations": [{"relation": r, "cible": c} for _, r, c in sortantes]}


if __name__ == "__main__":
    profil_test = {"serie_bac": "S", "note_maths": 5, "note_sciences": 4, "note_langues": 3,
                   "note_eco": 3, "matieres_preferees": ["Mathematiques", "Informatique / Technologie"],
                   "competences": ["Programmation", "Analyse de donnees / logique"],
                   "interets": ["Technologie / informatique", "Sciences"],
                   "environnement": "Bureau", "metiers_vises": ["Technique / ingenierie"]}
    print(json.dumps(analyser_profil_ml(profil_test), indent=1, ensure_ascii=False))
    print(json.dumps(verifier_prerequis("A2", "PIP", 2), indent=1, ensure_ascii=False))
    print(json.dumps(chemins_graphe("ISAIA"), indent=1, ensure_ascii=False))
