"""Recode les exports CSV Google Forms de l'enquete au format du dataset ML.

Usage (apres gel de l'enquete) :
    python data/enquete/recoder_reponses.py --unique export.csv
        formulaire unique v3 (aiguillage etudiant/professionnel integre)
    python data/enquete/recoder_reponses.py --etudiants a.csv --pros b.csv
        anciens formulaires separes (v2)

Sorties :
    data/enquete/reponses_recodees.csv   profils au format de data/synthetic/dataset.csv
                                         (+ colonnes population, satisfaction)
    data/enquete/reponses_ecartees.csv   lignes exclues, avec le motif (pour le registre)

Le reperage des colonnes se fait par mots-cles (les intitules exacts de Google
Forms varient) ; les valeurs sont normalisees vers le vocabulaire canonique du
dataset (sans accents). Toute transformation est reproductible et documentee
dans le registre de collecte (exigence du sujet).
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
    v = norm(valeur)
    if not v:
        return None
    for c in vocab:
        if norm(c) == v or norm(c) in v or v in norm(c):
            return c
    return None


def recoder_multi(cellule, vocab):
    tokens = []
    for part in re.split(r",\s*|;", str(cellule)):
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
    """population : 'etudiant', 'professionnel', ou None (formulaire unique v3 :
    la population est lue ligne a ligne dans la question d'aiguillage)."""
    with open(chemin, encoding="utf-8-sig", newline="") as fh:
        lecteur = csv.DictReader(fh)
        entetes = lecteur.fieldnames or []
        cols = {
            "aiguillage": trouver_colonne(entetes, "vous etes"),
            "serie": trouver_colonne(entetes, "serie"),
            "matieres": trouver_colonne(entetes, "matieres"),
            "competences": trouver_colonne(entetes, "competences"),
            "interets": trouver_colonne(entetes, "interet"),
            "environnement": trouver_colonne(entetes, "environnement"),
            "metiers": trouver_colonne(entetes, "metier", "vis") or trouver_colonne(entetes, "type de metier"),
            "note_maths": trouver_colonne(entetes, "[mathematiques]") or trouver_colonne(entetes, "niveau", "mathematiques"),
            "note_sciences": trouver_colonne(entetes, "sciences experimentales"),
            "note_langues": trouver_colonne(entetes, "langues et communication"),
            "note_eco": trouver_colonne(entetes, "economie-gestion"),
            "filiere_etu": trouver_colonne(entetes, "filiere", "parcours"),
            "filiere_pro": trouver_colonne(entetes, "domaine", "etude"),
            "satisf_etu": trouver_colonne(entetes, "satisfait"),
            "satisf_pro": trouver_colonne(entetes, "adaptee", "metier") or trouver_colonne(entetes, "avec le recul", "formation"),
        }
        essentielles = ["serie", "matieres", "interets", "environnement"]
        manquantes = [k for k in essentielles if cols[k] is None]
        if manquantes:
            print(f"[ATTENTION] {chemin} : colonnes non reperees {manquantes} — verifier les intitules.")

        def val(ligne, cle):
            col = cols.get(cle)
            return ligne.get(col, "") if col else ""

        n_ok = n_ko = 0
        for i, ligne in enumerate(lecteur, start=2):
            pop = population
            if pop is None:
                aig = norm(val(ligne, "aiguillage"))
                pop = ("professionnel" if "professionnel" in aig
                       else "etudiant" if "etudiant" in aig or "diplom" in aig else None)
            if pop is None:
                ecartees.append({"fichier": Path(chemin).name, "ligne": i, "population": "?",
                                 "motif": "population indeterminee (question d'aiguillage vide)",
                                 "valeur": val(ligne, "aiguillage")})
                n_ko += 1
                continue

            brut_filiere = val(ligne, "filiere_etu") if pop == "etudiant" else val(ligne, "filiere_pro")
            if not brut_filiere:  # secours : l'autre colonne
                brut_filiere = val(ligne, "filiere_pro") or val(ligne, "filiere_etu")
            filiere = extraire_sigle(brut_filiere)
            if not filiere:
                ecartees.append({"fichier": Path(chemin).name, "ligne": i, "population": pop,
                                 "motif": "filiere non rattachable a un parcours ISPM",
                                 "valeur": brut_filiere})
                n_ko += 1
                continue

            sortie.append({
                "id": f"{pop[:3]}-{i:04d}",
                "population": pop,
                "serie_bac": vers_canonique(val(ligne, "serie"), SERIES) or "",
                "note_maths": val(ligne, "note_maths") or 3,
                "note_sciences": val(ligne, "note_sciences") or 3,
                "note_langues": val(ligne, "note_langues") or 3,
                "note_eco": val(ligne, "note_eco") or 3,
                "matieres_preferees": recoder_multi(val(ligne, "matieres"), MATIERES),
                "competences": recoder_multi(val(ligne, "competences"), COMPETENCES),
                "interets": recoder_multi(val(ligne, "interets"), INTERETS),
                "environnement": vers_canonique(val(ligne, "environnement"), ENVIRONNEMENTS) or "",
                "metiers_vises": recoder_multi(val(ligne, "metiers"), METIERS),
                "filiere": filiere,
                "satisfaction": val(ligne, "satisf_etu") or val(ligne, "satisf_pro"),
            })
            n_ok += 1
        print(f"[OK] {chemin} : {n_ok} retenues, {n_ko} ecartees")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--unique", help="export CSV du formulaire unique v3 (aiguillage integre)")
    parser.add_argument("--etudiants", help="export CSV Google Forms etudiants (v2)")
    parser.add_argument("--pros", help="export CSV Google Forms professionnels (v2)")
    args = parser.parse_args()
    if not (args.unique or args.etudiants or args.pros):
        raise SystemExit("Fournir --unique export.csv (ou --etudiants/--pros pour l'ancien format)")

    sortie, ecartees = [], []
    if args.unique:
        recoder_fichier(args.unique, None, sortie, ecartees)
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

    etu = sum(1 for r in sortie if r["population"] == "etudiant")
    pro = len(sortie) - etu
    print(f"\nTotal retenu : {len(sortie)} ({etu} etudiants, {pro} professionnels) · ecarte : {len(ecartees)}")
    print("Etape suivante : python models/transfert_reel.py")
    print("Reporter ces chiffres dans data/enquete/registre_collecte.csv")


if __name__ == "__main__":
    main()
