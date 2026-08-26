"""Generateur de profils etudiants synthetiques pour l'entrainement du modele ML.

Usage :
    python data/synthetic/generateur.py --n 3000 --seed 42

Sortie :
    data/synthetic/dataset.csv

Principe (documente en detail dans DONNEES_SYNTHETIQUES.md) :
  1. On genere un profil realiste (serie de bac, notes, matieres preferees,
     competences, interets, environnement, metier vise) avec des correlations
     simples : on prefere ce ou l'on est bon, les competences suivent les matieres.
  2. On calcule un score d'affinite du profil pour chacune des 16 filieres de
     l'ISPM (regles d'affinite ci-dessous) en ne retenant que les filieres dont
     les conditions officielles de serie de bac sont satisfaites (source :
     inscription.php, voir data/registre_sources.csv).
  3. L'etiquette (filiere recommandee) est TIREE au hasard selon un softmax des
     scores, pas un argmax : cela introduit un bruit d'etiquette voulu, comme
     dans la realite ou deux candidats identiques choisissent parfois des
     filieres differentes.

Le vocabulaire des champs est STRICTEMENT ALIGNE sur le questionnaire d'enquete
(ENQUETE-QUESTIONNAIRES.md) afin que le modele entraine sur ce jeu puisse etre
valide/teste sur les reponses reelles sans recodage.
"""

import argparse
import csv
import math
import random
from pathlib import Path

# ---------------------------------------------------------------- vocabulaire
MATIERES = ["Mathematiques", "Physique-Chimie", "SVT", "Informatique / Technologie",
            "Francais / Litterature", "Langues etrangeres", "Histoire-Geographie",
            "Economie / Gestion", "Arts", "Sport"]
COMPETENCES = ["Programmation", "Analyse de donnees / logique", "Redaction / communication",
               "Creativite / design", "Organisation / gestion de projet", "Vente / negociation",
               "Electronique / bricolage technique", "Travail en equipe"]
INTERETS = ["Technologie / informatique", "Sciences", "Entrepreneuriat / business",
            "Finance / comptabilite", "Art / design / audiovisuel", "Communication / medias",
            "Tourisme / hotellerie", "Agriculture / environnement", "BTP / construction",
            "Sante / social", "Droit / justice"]
ENVIRONNEMENTS = ["Bureau", "Terrain / exterieur", "Laboratoire", "Atelier / usine", "Mixte"]
METIERS = ["Technique / ingenierie", "Gestion / management", "Creation / design",
           "Commerce / relation client", "Recherche / enseignement", "Entrepreneur / independant"]
SERIES = ["A1", "A2", "C", "D", "S", "L", "Technique industrielle",
          "Technique genie civil", "Technique agricole"]
SERIES_POIDS = [8, 12, 15, 25, 20, 8, 6, 3, 3]  # hypothese : D et S majoritaires

TOUTES = set(SERIES)
SCIENTIFIQUES = {"C", "D", "S"}

# Conditions officielles d'acces par filiere (source : inscription.php).
# A2 accepte en biotechnologie si note de maths suffisante (>= 12/20, soit >= 3/5 ici).
ELIGIBILITE = {
    "IGGLIA":  SCIENTIFIQUES | {"Technique industrielle"},
    "ESIIA":   SCIENTIFIQUES | {"Technique industrielle"},
    "IMTICIA": SCIENTIFIQUES | {"Technique industrielle"},
    "ISAIA":   SCIENTIFIQUES | {"Technique industrielle"},
    "CAA": TOUTES, "FIC": TOUTES, "DTJA": TOUTES, "EMP": TOUTES,
    "IAA": SCIENTIFIQUES | {"Technique agricole", "A2"},
    "PIP": SCIENTIFIQUES | {"Technique agricole", "A2"},
    "AEE": SCIENTIFIQUES | {"Technique agricole", "A2"},
    "EMII": SCIENTIFIQUES | {"Technique industrielle"},
    "ICMP": SCIENTIFIQUES | {"Technique industrielle"},
    "GCA":  SCIENTIFIQUES | {"Technique genie civil"},
    "TEE": TOUTES, "TEH": TOUTES,
}

# Regles d'affinite : poids additifs par element de profil present.
# Cles : m = matiere preferee, c = competence, i = interet, e = environnement,
# j = metier vise, notes = poids applique a (note - 3) pour chaque grille de notes.
AFFINITES = {
    "IGGLIA":  {"m": {"Informatique / Technologie": 3, "Mathematiques": 2},
                "c": {"Programmation": 3, "Analyse de donnees / logique": 2},
                "i": {"Technologie / informatique": 3},
                "e": {"Bureau": 1}, "j": {"Technique / ingenierie": 2},
                "notes": {"maths": 1.5}},
    "ESIIA":   {"m": {"Informatique / Technologie": 2, "Physique-Chimie": 2, "Mathematiques": 1},
                "c": {"Electronique / bricolage technique": 3, "Programmation": 1.5},
                "i": {"Technologie / informatique": 2, "Sciences": 1},
                "e": {"Atelier / usine": 1, "Laboratoire": 1}, "j": {"Technique / ingenierie": 2},
                "notes": {"maths": 1, "sciences": 1}},
    "IMTICIA": {"m": {"Informatique / Technologie": 2, "Arts": 1.5},
                "c": {"Creativite / design": 2.5, "Programmation": 1.5, "Redaction / communication": 1},
                "i": {"Art / design / audiovisuel": 2.5, "Communication / medias": 2.5,
                      "Technologie / informatique": 1.5},
                "e": {"Bureau": 1}, "j": {"Creation / design": 2},
                "notes": {}},
    "ISAIA":   {"m": {"Mathematiques": 3, "Informatique / Technologie": 1.5, "Economie / Gestion": 1},
                "c": {"Analyse de donnees / logique": 3, "Programmation": 1},
                "i": {"Finance / comptabilite": 1.5, "Sciences": 1.5, "Technologie / informatique": 1.5},
                "e": {"Bureau": 1}, "j": {"Technique / ingenierie": 1, "Recherche / enseignement": 1},
                "notes": {"maths": 2.5}},
    "CAA":     {"m": {"Economie / Gestion": 2, "Langues etrangeres": 1},
                "c": {"Vente / negociation": 3, "Redaction / communication": 1.5, "Travail en equipe": 1},
                "i": {"Entrepreneuriat / business": 3, "Communication / medias": 1},
                "e": {"Bureau": 0.5, "Mixte": 0.5},
                "j": {"Commerce / relation client": 2.5, "Entrepreneur / independant": 1.5},
                "notes": {"eco": 1}},
    "FIC":     {"m": {"Economie / Gestion": 2.5, "Mathematiques": 1.5},
                "c": {"Analyse de donnees / logique": 1.5, "Organisation / gestion de projet": 2},
                "i": {"Finance / comptabilite": 3},
                "e": {"Bureau": 1.5}, "j": {"Gestion / management": 2},
                "notes": {"eco": 1.5, "maths": 1}},
    "DTJA":    {"m": {"Francais / Litterature": 2, "Histoire-Geographie": 1.5, "Langues etrangeres": 1},
                "c": {"Redaction / communication": 2.5},
                "i": {"Droit / justice": 3.5},
                "e": {"Bureau": 1}, "j": {"Gestion / management": 1},
                "notes": {"langues": 1.5}},
    "EMP":     {"m": {"Economie / Gestion": 2.5, "Histoire-Geographie": 1},
                "c": {"Organisation / gestion de projet": 2.5, "Analyse de donnees / logique": 1},
                "i": {"Entrepreneuriat / business": 1.5, "Finance / comptabilite": 1},
                "e": {"Mixte": 0.5}, "j": {"Gestion / management": 2.5},
                "notes": {"eco": 2}},
    "IAA":     {"m": {"SVT": 2, "Physique-Chimie": 2},
                "c": {"Analyse de donnees / logique": 0.5, "Organisation / gestion de projet": 1},
                "i": {"Sciences": 2, "Agriculture / environnement": 1.5},
                "e": {"Laboratoire": 1.5, "Atelier / usine": 1}, "j": {"Technique / ingenierie": 1},
                "notes": {"sciences": 1.5}},
    "PIP":     {"m": {"SVT": 3, "Physique-Chimie": 2},
                "c": {"Analyse de donnees / logique": 1},
                "i": {"Sante / social": 2.5, "Sciences": 2},
                "e": {"Laboratoire": 2.5}, "j": {"Recherche / enseignement": 1.5},
                "notes": {"sciences": 2}},
    "AEE":     {"m": {"SVT": 2.5},
                "c": {"Travail en equipe": 1, "Organisation / gestion de projet": 1},
                "i": {"Agriculture / environnement": 3.5, "Entrepreneuriat / business": 1},
                "e": {"Terrain / exterieur": 2.5}, "j": {"Entrepreneur / independant": 1.5},
                "notes": {"sciences": 1}},
    "EMII":    {"m": {"Physique-Chimie": 2.5, "Mathematiques": 1.5, "Informatique / Technologie": 1},
                "c": {"Electronique / bricolage technique": 3},
                "i": {"Technologie / informatique": 1.5, "BTP / construction": 1},
                "e": {"Atelier / usine": 2.5}, "j": {"Technique / ingenierie": 2},
                "notes": {"maths": 1, "sciences": 1.5}},
    "GCA":     {"m": {"Mathematiques": 2, "Physique-Chimie": 1.5, "Arts": 1},
                "c": {"Creativite / design": 1.5, "Organisation / gestion de projet": 1},
                "i": {"BTP / construction": 3.5},
                "e": {"Terrain / exterieur": 1.5, "Mixte": 1}, "j": {"Technique / ingenierie": 2},
                "notes": {"maths": 1.5}},
    "ICMP":    {"m": {"Physique-Chimie": 3, "Mathematiques": 1.5},
                "c": {"Analyse de donnees / logique": 1},
                "i": {"Sciences": 2, "BTP / construction": 1},
                "e": {"Laboratoire": 1.5, "Terrain / exterieur": 1.5}, "j": {"Technique / ingenierie": 2},
                "notes": {"sciences": 2}},
    "TEE":     {"m": {"Histoire-Geographie": 2, "Langues etrangeres": 2, "SVT": 1},
                "c": {"Redaction / communication": 1.5, "Travail en equipe": 1},
                "i": {"Tourisme / hotellerie": 3, "Agriculture / environnement": 1.5},
                "e": {"Terrain / exterieur": 2}, "j": {"Commerce / relation client": 1},
                "notes": {"langues": 1.5}},
    "TEH":     {"m": {"Langues etrangeres": 2.5, "Histoire-Geographie": 1},
                "c": {"Travail en equipe": 1.5, "Vente / negociation": 1, "Creativite / design": 1},
                "i": {"Tourisme / hotellerie": 3.5},
                "e": {"Mixte": 1, "Terrain / exterieur": 1}, "j": {"Commerce / relation client": 1.5},
                "notes": {"langues": 2}},
}

FILIERES = list(AFFINITES)

# Correlations simples matiere -> competences et matiere -> interets probables.
MATIERE_VERS_COMPETENCE = {
    "Informatique / Technologie": ["Programmation", "Electronique / bricolage technique"],
    "Mathematiques": ["Analyse de donnees / logique"],
    "Physique-Chimie": ["Electronique / bricolage technique", "Analyse de donnees / logique"],
    "Francais / Litterature": ["Redaction / communication"],
    "Langues etrangeres": ["Redaction / communication"],
    "Economie / Gestion": ["Organisation / gestion de projet", "Vente / negociation"],
    "Arts": ["Creativite / design"],
    "Sport": ["Travail en equipe"],
}
MATIERE_VERS_INTERET = {
    "Informatique / Technologie": ["Technologie / informatique"],
    "Mathematiques": ["Sciences", "Finance / comptabilite"],
    "Physique-Chimie": ["Sciences", "BTP / construction"],
    "SVT": ["Sante / social", "Agriculture / environnement", "Sciences"],
    "Economie / Gestion": ["Entrepreneuriat / business", "Finance / comptabilite"],
    "Histoire-Geographie": ["Droit / justice", "Tourisme / hotellerie"],
    "Langues etrangeres": ["Tourisme / hotellerie", "Communication / medias"],
    "Arts": ["Art / design / audiovisuel", "Communication / medias"],
    "Francais / Litterature": ["Communication / medias", "Droit / justice"],
}


def note(rng, mu):
    """Note 1..5 centree sur mu avec bruit gaussien."""
    return max(1, min(5, round(rng.gauss(mu, 0.9))))


def generer_profil(rng):
    serie = rng.choices(SERIES, weights=SERIES_POIDS)[0]
    scientifique = serie in SCIENTIFIQUES or serie.startswith("Technique")
    notes = {
        "maths": note(rng, 3.6 if serie in {"C", "S"} else 3.1 if scientifique else 2.5),
        "sciences": note(rng, 3.5 if scientifique else 2.6),
        "langues": note(rng, 3.4 if serie in {"A1", "A2", "L"} else 3.0),
        "eco": note(rng, 3.3 if serie in {"A1", "A2", "L"} else 2.9),
    }
    # On prefere plutot ce ou l'on est bon (poids = note), plus une part de hasard.
    poids_matieres = []
    for m in MATIERES:
        if m == "Mathematiques":
            w = notes["maths"]
        elif m in {"Physique-Chimie", "SVT"}:
            w = notes["sciences"]
        elif m in {"Langues etrangeres", "Francais / Litterature"}:
            w = notes["langues"]
        elif m in {"Economie / Gestion", "Histoire-Geographie"}:
            w = notes["eco"]
        else:
            w = 3
        poids_matieres.append(w + rng.uniform(0, 2))
    k_mat = rng.choice([2, 3])
    matieres = weighted_sample(rng, MATIERES, poids_matieres, k_mat)

    competences = biased_pick(rng, COMPETENCES, matieres, MATIERE_VERS_COMPETENCE, rng.randint(2, 4))
    interets = biased_pick(rng, INTERETS, matieres, MATIERE_VERS_INTERET, rng.randint(2, 4))
    return {
        "serie_bac": serie, **{f"note_{k}": v for k, v in notes.items()},
        "matieres_preferees": matieres, "competences": competences, "interets": interets,
        "environnement": rng.choices(ENVIRONNEMENTS, weights=[30, 20, 12, 12, 26])[0],
        "metiers_vises": weighted_sample(rng, METIERS, [1] * len(METIERS), rng.choice([1, 2])),
    }


def weighted_sample(rng, items, weights, k):
    """Tirage sans remise pondere."""
    items, weights, out = list(items), list(weights), []
    for _ in range(min(k, len(items))):
        pick = rng.choices(range(len(items)), weights=weights)[0]
        out.append(items.pop(pick))
        weights.pop(pick)
    return out


def biased_pick(rng, vocab, matieres, mapping, k):
    poids = {v: 1.0 for v in vocab}
    for m in matieres:
        for v in mapping.get(m, []):
            poids[v] += 2.5
    return weighted_sample(rng, vocab, [poids[v] for v in vocab], k)


def score(profil, filiere):
    a = AFFINITES[filiere]
    s = 0.0
    s += sum(w for m, w in a["m"].items() if m in profil["matieres_preferees"])
    s += sum(w for c, w in a["c"].items() if c in profil["competences"])
    s += sum(w for i, w in a["i"].items() if i in profil["interets"])
    s += a["e"].get(profil["environnement"], 0)
    s += sum(w for j, w in a["j"].items() if j in profil["metiers_vises"])
    s += sum(w * (profil[f"note_{n}"] - 3) for n, w in a["notes"].items())
    return s


def eligibles(profil):
    out = []
    for f in FILIERES:
        if profil["serie_bac"] not in ELIGIBILITE[f]:
            continue
        # Regle officielle : A2 admis en biotechnologie si maths >= 12/20 (~3/5).
        if profil["serie_bac"] == "A2" and f in {"IAA", "PIP", "AEE"} and profil["note_maths"] < 3:
            continue
        out.append(f)
    return out


def choisir_label(rng, profil, temperature=1.2):
    """Softmax sur les scores des filieres eligibles -> bruit d'etiquette voulu."""
    cands = eligibles(profil)
    scores = [score(profil, f) / temperature for f in cands]
    m = max(scores)
    expo = [math.exp(s - m) for s in scores]
    total = sum(expo)
    return rng.choices(cands, weights=[e / total for e in expo])[0]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=3000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", default=str(Path(__file__).with_name("dataset.csv")))
    args = parser.parse_args()
    rng = random.Random(args.seed)

    rows, compte = [], {}
    for i in range(args.n):
        p = generer_profil(rng)
        label = choisir_label(rng, p)
        compte[label] = compte.get(label, 0) + 1
        rows.append({
            "id": f"syn-{i:05d}", "serie_bac": p["serie_bac"],
            "note_maths": p["note_maths"], "note_sciences": p["note_sciences"],
            "note_langues": p["note_langues"], "note_eco": p["note_eco"],
            "matieres_preferees": "|".join(p["matieres_preferees"]),
            "competences": "|".join(p["competences"]),
            "interets": "|".join(p["interets"]),
            "environnement": p["environnement"],
            "metiers_vises": "|".join(p["metiers_vises"]),
            "filiere": label,
        })

    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    print(f"[OK] {args.n} profils -> {args.out} (seed={args.seed})")
    print("Repartition des etiquettes :")
    for f in sorted(compte, key=compte.get, reverse=True):
        pct = 100 * compte[f] / args.n
        drapeau = "  <-- classe rare" if pct < 2 else ""
        print(f"  {f:8s} {compte[f]:5d}  ({pct:4.1f}%){drapeau}")


if __name__ == "__main__":
    main()
