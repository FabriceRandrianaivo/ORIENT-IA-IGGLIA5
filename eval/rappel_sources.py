"""Mesure du rappel des sources utiles (dimension 'Recherche documentaire', sujet §14).

Pour un jeu de questions-or dont on connait la source officielle attendue, on
verifie que la recherche hybride remonte cette source en position 1 (hit@1) et
dans le top-3 (hit@3).

Usage :
    python eval/rappel_sources.py   ->  eval/RAPPEL-SOURCES.md
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "rag"))
from moteur import Recherche  # noqa: E402

ICI = Path(__file__).resolve().parent

# (question, sources attendues — au moins une doit apparaitre)
JEU_OR = [
    ("Quelles séries de bac permettent d'entrer en biotechnologie ?", {"src-inscription"}),
    ("Quels diplômes délivre l'ISPM ?", {"src-brochure-papier"}),
    ("Quels sont les débouchés de la filière ISAIA ?", {"src-filieres", "src-inscription"}),
    ("Quels sont les frais de demande de transfert ?", {"src-brochure-papier"}),
    ("Quand l'ISPM a-t-il été créé ?", {"src-brochure-papier", "src-presentation"}),
    ("Quels prix l'ISPM a-t-il obtenus en 2024 ?", {"src-brochure-papier"}),
    ("Quelles sont les conditions d'accès en première année ?", {"src-inscription", "src-brochure-papier"}),
    ("Que fait la filière Génie Civil et Architecture GCA ?", {"src-filieres", "src-inscription"}),
    ("Quels laboratoires et infrastructures possède le campus ?", {"src-brochure-papier"}),
    ("Quelle est l'adresse et le téléphone de l'ISPM ?", {"src-accueil", "src-brochure", "src-brochure-papier"}),
    ("Existe-t-il des passerelles entre les formations ?", {"src-brochure-papier"}),
    ("Quel est le taux d'embauche des diplômés ?", {"src-accueil", "src-brochure", "src-brochure-papier"}),
]


def main():
    recherche = Recherche()
    lignes, hit1 = [], 0
    hit3 = 0
    for question, attendues in JEU_OR:
        passages = recherche.rechercher(question, 3)
        sources_top1 = set(passages[0]["sources"]) if passages else set()
        sources_top3 = {s for p in passages for s in p["sources"]}
        h1 = bool(attendues & sources_top1)
        h3 = bool(attendues & sources_top3)
        hit1 += h1
        hit3 += h3
        lignes.append(f"| {question} | {', '.join(sorted(attendues))} | "
                      f"{'✅' if h1 else '—'} | {'✅' if h3 else '❌ ' + ', '.join(sorted(sources_top3))} |")
        print(f"{'OK ' if h3 else 'KO '} hit@1={'oui' if h1 else 'non'}  {question}")

    n = len(JEU_OR)
    md = ["# Rappel des sources utiles — recherche documentaire",
          "", f"Jeu de {n} questions-or (source officielle attendue connue). "
          f"**hit@1 : {hit1}/{n} ({100 * hit1 // n} %) · hit@3 : {hit3}/{n} ({100 * hit3 // n} %)**",
          "", "| Question | Source attendue | hit@1 | hit@3 |", "|---|---|---|---|", *lignes,
          "", "Reproduire : `python eval/rappel_sources.py` (index hybride BM25 + TF-IDF)."]
    (ICI / "RAPPEL-SOURCES.md").write_text("\n".join(md), encoding="utf-8")
    print(f"\nhit@1 : {hit1}/{n} · hit@3 : {hit3}/{n} -> RAPPEL-SOURCES.md")


if __name__ == "__main__":
    main()
