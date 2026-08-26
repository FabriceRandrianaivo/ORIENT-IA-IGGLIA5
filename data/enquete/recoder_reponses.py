"""Recode les exports CSV Google Forms de l'enquete au format du dataset ML.

Usage (apres gel de l'enquete) :
    python data/enquete/recoder_reponses.py --etudiants export_etudiants.csv --pros export_pros.csv

Sorties :
    data/enquete/reponses_recodees.csv   profils au format de data/synthetic/dataset.csv
                                         (+ colonnes population, satisfaction)
    data/enquete/reponses_ecartees.csv   lignes exclues, avec le motif (pour le registre)

Le reperage des colonnes se fait par mots-cles (les intitules exacts de Google
Forms varient) ; les valeurs sont normalisees vers le vocabulaire canonique du
dataset (sans accents). Toute transformation est donc reproductible et
documentable dans le registre de collecte (exigence du sujet).
"""

import argparse
import csv
import re
import unicodedata
from pathlib import Path

ICI = Path(__file__).resolve().parent

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
SIGLES = ["IGGLIA", "ESIIA", "IMTICIA", "ISAIA", "CAA", "FIC", "DTJA", "EMP",
          "IAA", "PIP", "AEE", "EMII", "GCA", "ICMP", "TEE", "TEH"]

# Pour les professionnels (filiere en texte libre) : mots-cles -> sigle.
MOTS_CLES_FILIERE = {
    "informatique de gestion": "IGGLIA", "genie logiciel": "IGGLIA", "igglia": "IGGLIA",
    "electronique": "ESIIA", "esiia": "ESIIA",
    "multimedia": "IMTICIA", "imtic": "IMTICIA", "telecommunication": "IMTICIA",
    "statistique": "ISAIA", "isaia": "ISAIA",
    "commerce": "CAA", "marketing": "CAA", "administration des affaires": "CAA",
    "finance": "FIC", "comptabilite": "FIC",
    "droit": "DTJA", "juridique": "DTJA",
    "economie": "EMP", "management de projet": "EMP",
    "agroalimentaire": "IAA",
    "pharma": "PIP",
    "agriculture": "AEE", "elevage": "AEE", "agronomie": "AEE",
    "electromecanique": "EMII", "informatique industrielle": "EMII", "mecanique": "EMII",
    "genie civil": "GCA", "architecture": "GCA", "batiment": "GCA",
    "chimie": "ICMP", "mine": "ICMP", "petrol": "ICMP",
    "environnement": "TEE",
    "hotellerie": "TEH", "tourisme": "TEH", "cuisine": "TEH",
}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFD", str(s).lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn").strip()


def trouver_colonne(entetes, *mots):
    """Premiere colonne dont l'intitule contient tous les mots donnes."""
    for e in entetes:
        if all(m in norm(e) for m in mots):
            return e
    return None


def vers_canonique(valeur, vocab):
    """Rapproche une valeur Forms (accents, variantes) du vocabulaire canonique."""
    v = norm(valeur)
    for c in vocab:
        if norm(c) == v or norm(c) in v or v in norm(c):
            return c
    return None


def recoder_multi(cellule, vocab):
    tokens = []
    for part in re.split(r",\s*(?=[A-ZÉÈ])|;", str(cellule)):
        c = vers_canonique(part, vocab)
        if c and c not in tokens:
            tokens.append(c)
    return "|".join(tokens)


def extraire_sigle(valeur):
    v = str(valeur).upper()
    for s in SIGLES:
        if s in v:
            return s
    v_norm = norm(valeur)
    for mot, sigle in MOTS_CLES_FILIERE.items():
        if mot in v_norm:
            return sigle
    return None


def recoder_fichier(chemin, population, sortie, ecartees):
    with open(chemin, encoding="utf-8-sig", newline="") as fh:
        lecteur = csv.DictReader(fh)
        entetes = lecteur.fieldnames or []
        cols = {
            "serie": trouver_colonne(entetes, "serie"),
            "matieres": trouver_colonne(entetes, "matieres"),
            "competences": trouver_colonne(entetes, "competences"),
            "interets": trouver_colonne(entetes, "interet"),
            "environnement": trouver_colonne(entetes, "environnement"),
            "metiers": trouver_colonne(entetes, "metier", "vis") or trouver_colonne(entetes, "type de metier"),
            "note_maths": trouver_colonne(entetes, "niveau", "mathematiques") or trouver_colonne(entetes, "[mathematiques]"),
            "note_sciences": trouver_colonne(entetes, "sciences experimentales"),
            "note_langues": trouver_colonne(entetes, "langues et communication"),
            "note_eco": trouver_colonne(entetes, "economie-gestion"),
            "filiere": (trouver_colonne(entetes, "filiere", "parcours")
                        or trouver_colonne(entetes, "domaine", "etude")),
            "satisfaction": (trouver_colonne(entetes, "satisfait")
                             or trouver_colonne(entetes, "adaptee", "metier")),
        }
        manquantes = [k for k, v in cols.items() if v is None]
        if manquantes:
            print(f"[ATTENTION] {chemin} : colonnes non reperees {manquantes} — verifier les intitules.")

        n_ok = n_ko = 0
        for i, ligne in enumerate(lecteur, start=2):
            filiere = extraire_sigle(ligne.get(cols["filiere"] or "", ""))
            if not filiere:
                ecartees.append({"fichier": Path(chemin).name, "ligne": i, "population": population,
                                 "motif": "filiere non rattachable a un parcours ISPM",
                                 "valeur": ligne.get(cols["filiere"] or "", "")})
                n_ko += 1
                continue
            serie = vers_canonique(ligne.get(cols["serie"] or "", ""), SERIES) or ""
            sortie.append({
                "id": f"{population[:3]}-{i:04d}",
                "population": population,
                "serie_bac": serie,
                "note_maths": ligne.get(cols["note_maths"] or "", 3) or 3,
                "note_sciences": ligne.get(cols["note_sciences"] or "", 3) or 3,
                "note_langues": ligne.get(cols["note_langues"] or "", 3) or 3,
                "note_eco": ligne.get(cols["note_eco"] or "", 3) or 3,
                "matieres_preferees": recoder_multi(ligne.get(cols["matieres"] or "", ""), MATIERES),
                "competences": recoder_multi(ligne.get(cols["competences"] or "", ""), COMPETENCES),
                "interets": recoder_multi(ligne.get(cols["interets"] or "", ""), INTERETS),
                "environnement": vers_canonique(ligne.get(cols["environnement"] or "", ""), ENVIRONNEMENTS) or "",
                "metiers_vises": recoder_multi(ligne.get(cols["metiers"] or "", ""), METIERS),
                "filiere": filiere,
                "satisfaction": ligne.get(cols["satisfaction"] or "", ""),
            })
            n_ok += 1
        print(f"[OK] {chemin} ({population}) : {n_ok} retenues, {n_ko} ecartees")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--etudiants", help="export CSV Google Forms etudiants")
    parser.add_argument("--pros", help="export CSV Google Forms professionnels")
    args = parser.parse_args()
    if not args.etudiants and not args.pros:
        raise SystemExit("Fournir au moins un export : --etudiants et/ou --pros")

    sortie, ecartees = [], []
    if args.etudiants:
        recoder_fichier(args.etudiants, "etudiant", sortie, ecartees)
    if args.pros:
        recoder_fichier(args.pros, "professionnel", sortie, ecartees)

    if sortie:
        with (ICI / "reponses_recodees.csv").open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(sortie[0]))
            writer.writeheader()
            writer.writerows(sortie)
    if ecartees:
        with (ICI / "reponses_ecartees.csv").open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(ecartees[0]))
            writer.writeheader()
            writer.writerows(ecartees)

    print(f"\nTotal retenu : {len(sortie)} · ecarte : {len(ecartees)}")
    print("Etape suivante : python models/transfert_reel.py "
          "(puis --population etudiant / professionnel pour le detail)")
    print("Reporter les chiffres dans le registre de collecte.")


if __name__ == "__main__":
    main()
