"""Moteur de recherche documentaire hybride d'ORIENT'IA.

Recherche hybride : BM25 (lexicale) + TF-IDF cosinus (vectorielle), scores
combines a parts egales apres normalisation. Le corpus est petit (site ISPM),
l'index est reconstruit en memoire au demarrage (< 1 s) — pas de base externe.

Chaque passage porte l'identifiant de sa source (voir data/registre_sources.csv)
pour que l'assistant cite des references verifiables.
"""

import json
import re
import unicodedata
from pathlib import Path

from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parents[1]


def _normaliser(texte: str) -> list:
    """Minuscules, sans accents, pluriels replies (banques -> banque) pour que
    singulier et pluriel se retrouvent (pas de stemming lourd necessaire)."""
    texte = unicodedata.normalize("NFD", texte.lower())
    texte = "".join(c for c in texte if unicodedata.category(c) != "Mn")
    return [t.rstrip("s") if len(t) > 3 else t for t in re.findall(r"[a-z0-9]+", texte)]


SYNONYMES = {"carriere": "debouches metiers", "job": "metier",
             "emploi": "metier debouches", "travail": "metier",
             "universite": "institut", "fac": "institut",
             "cursus": "cursus diplomes", "professeur": "enseignant",
             "matiere": "matieres enseigne"}


def etendre(question: str) -> str:
    """Expansion de synonymes : rapproche le vocabulaire de l'utilisateur
    (carriere, job, universite) de celui du corpus (debouches, metier, institut).
    La comparaison se fait sans accents (carrieres == carrières)."""
    q_plate = unicodedata.normalize("NFD", question.lower())
    q_plate = "".join(c for c in q_plate if unicodedata.category(c) != "Mn")
    for mot, expansion in SYNONYMES.items():
        if re.search(rf"\b{mot}s?\b", q_plate):
            question = f"{question} {expansion}"
    return question


def construire_chunks() -> list:
    """Corpus = pages du site (paragraphes) + fiches filieres structurees."""
    chunks = []

    # 1. Fiches filieres depuis formations.json (les plus utiles, une par filiere).
    data = json.loads((ROOT / "data" / "formations.json").read_text(encoding="utf-8"))
    for f in data["filieres"]:
        texte = (f"La filiere {f['sigle']} — {f['nom']} — appartient au departement "
                 f"{f['departement']}. {f['description']} Prerequis de bac : {f['prerequis_bac']}. "
                 f"Cette filiere prepare aux metiers et debouches suivants : "
                 f"{', '.join(f['debouches'] or ['non precises'])}.")
        chunks.append({"id": f"fiche-{f['sigle']}", "titre": f"Fiche {f['sigle']}",
                       "texte": texte, "sources": f["sources"]})

    acces = data["conditions_acces_premiere_annee"]
    chunks.append({"id": "fiche-acces", "titre": "Conditions d'acces en premiere annee",
                   "texte": ("Conditions d'acces et inscription en premiere annee a l'ISPM. "
                             f"{acces['modalite']} Documents : {'; '.join(acces['documents'])}. "
                             f"Frais de selection de dossier : {acces['frais_selection_dossier']}."),
                   "sources": [acces["source"]]})
    chunks.append({"id": "fiche-acces-series", "titre": "Series de bac exigees par departement",
                   "texte": ("Series de bac permettant d'entrer dans chaque departement de l'ISPM. "
                             + " ".join(f"{k} : {v}." for k, v in acces["series_bac_par_departement"].items())),
                   "sources": [acces["source"]]})
    etab = data["etablissement"]
    chunks.append({"id": "fiche-etablissement", "titre": "L'etablissement ISPM",
                   "texte": (f"Informations generales et presentation de l'institut : {etab['nom']}. "
                             f"Recteur : {etab.get('recteur', 'non precise')}. "
                             f"Adresse : {etab['adresse']}. "
                             f"Telephones : {', '.join(etab['telephones'])}. Email : {etab['email']}. "
                             f"Site web : {etab.get('site_web', '')}. {etab.get('reconnaissance', '')} "
                             f"Devise : {etab['devise']}. " + " ".join(etab["faits_notables"])),
                   "sources": etab["sources"]})

    pas = data.get("passerelles", {})
    if pas:
        chunks.append({"id": "fiche-passerelles", "titre": "Passerelles et transferts entre formations",
                       "texte": "Passerelles entre formations et transferts : " + pas["note"],
                       "sources": [pas["source"]]})

    cursus = data["cursus"]
    chunks.append({"id": "fiche-cursus", "titre": "Cursus et diplomes",
                   "texte": (cursus.get("systeme", "") + " Diplomes delivres : "
                             + " ; ".join(f"{d['nom']} ({d['niveau']})" for d in cursus["diplomes"]) + "."),
                   "sources": [cursus["source"]]})

    # 2. Pages du site en texte, decoupees en blocs de paragraphes (~600 caracteres).
    for txt in sorted((ROOT / "data" / "corpus" / "txt").glob("*.txt")):
        source = f"src-{txt.stem}"
        lignes = [l for l in txt.read_text(encoding="utf-8").split("\n") if len(l) > 40]
        bloc, n = "", 0
        for ligne in lignes:
            bloc = (bloc + " " + ligne).strip()
            if len(bloc) > 600:
                chunks.append({"id": f"{txt.stem}-{n}", "titre": f"Page {txt.stem}",
                               "texte": bloc, "sources": [source]})
                bloc, n = "", n + 1
        if len(bloc) > 80:
            chunks.append({"id": f"{txt.stem}-{n}", "titre": f"Page {txt.stem}",
                           "texte": bloc, "sources": [source]})
    return chunks


class Recherche:
    def __init__(self):
        self.chunks = construire_chunks()
        corpus_tokens = [_normaliser(c["texte"]) for c in self.chunks]
        self.bm25 = BM25Okapi(corpus_tokens)
        self.tfidf = TfidfVectorizer(tokenizer=_normaliser, token_pattern=None)
        self.matrice = self.tfidf.fit_transform(c["texte"] for c in self.chunks)

    def rechercher(self, question: str, k: int = 5) -> list:
        question = etendre(question)
        tokens = _normaliser(question)
        s_bm = self.bm25.get_scores(tokens)
        s_bm = s_bm / (s_bm.max() or 1.0)
        s_tf = cosine_similarity(self.tfidf.transform([question]), self.matrice)[0]
        s_tf = s_tf / (s_tf.max() or 1.0)
        scores = 0.5 * s_bm + 0.5 * s_tf
        meilleurs = scores.argsort()[::-1][:k]
        return [{"id": self.chunks[i]["id"], "titre": self.chunks[i]["titre"],
                 "texte": self.chunks[i]["texte"], "sources": self.chunks[i]["sources"],
                 "score": round(float(scores[i]), 4)}
                for i in meilleurs if scores[i] > 0.05]


if __name__ == "__main__":
    r = Recherche()
    print(f"{len(r.chunks)} passages indexes.")
    for p in r.rechercher("quelles conditions de bac pour la filiere informatique ?", 3):
        print(f"  [{p['score']}] {p['titre']} ({','.join(p['sources'])}) : {p['texte'][:110]}...")
