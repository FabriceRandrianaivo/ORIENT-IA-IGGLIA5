"""Harnais d'evaluation ORIENT'IA : rejoue les cas de eval_cases.jsonl contre l'agent.

Usage :
    python eval/run_eval.py

Sorties :
    eval/eval_results.csv    resultat detaille par cas
    eval/RESULTATS.md        synthese par categorie + latences (preuve mesuree)

Les verifications par cas (champ "attendu") :
    refus           l'agent doit refuser avec ce motif exact (injection, ...)
    contient        toutes ces chaines doivent apparaitre (insensible casse/accents)
    contient_un_de  au moins une de ces chaines
    pas_contient    aucune de ces chaines
    cite_source     la reponse cite au moins un identifiant de source (src-...)
"""

import csv
import json
import re
import statistics
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent"))
import agent  # noqa: E402

ICI = Path(__file__).resolve().parent


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFD", str(s).lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def verifier(attendu: dict, resultat: dict):
    """Renvoie (reussi, motifs_echec)."""
    rep = _norm(resultat["reponse"])
    motifs = []
    if "refus" in attendu and resultat["refus"] != attendu["refus"]:
        motifs.append(f"refus attendu={attendu['refus']} obtenu={resultat['refus']}")
    for aiguille in attendu.get("contient", []):
        if _norm(aiguille) not in rep:
            motifs.append(f"manque '{aiguille}'")
    if attendu.get("contient_un_de") and not any(_norm(a) in rep for a in attendu["contient_un_de"]):
        motifs.append(f"aucun de {attendu['contient_un_de']}")
    for aiguille in attendu.get("pas_contient", []):
        if _norm(aiguille) in rep:
            motifs.append(f"contient interdit '{aiguille}'")
    if attendu.get("cite_source") and not re.search(r"src-", resultat["reponse"]):
        motifs.append("aucune source citee (src-...)")
    return (not motifs, motifs)


def main():
    cas = [json.loads(l) for l in (ICI / "eval_cases.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    lignes, latences = [], []
    for c in cas:
        r = agent.repondre(c["question"], c.get("profil") or {})
        ok, motifs = verifier(c["attendu"], r)
        latences.append(r["latence_ms"])
        lignes.append({"id": c["id"], "categorie": c["categorie"], "reussi": ok,
                       "motifs_echec": " ; ".join(motifs), "refus": r["refus"] or "",
                       "latence_ms": r["latence_ms"], "mode": r["mode"],
                       "outils": "|".join(a["outil"] for a in r["outils"])})
        print(f"{'OK ' if ok else 'KO '} {c['id']:9s} [{c['categorie']}] {' ; '.join(motifs)}")

    with (ICI / "eval_results.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(lignes[0]))
        writer.writeheader()
        writer.writerows(lignes)

    # Synthese par categorie.
    cats = {}
    for l in lignes:
        cats.setdefault(l["categorie"], []).append(l["reussi"])
    total_ok = sum(l["reussi"] for l in lignes)
    md = [f"# Résultats d'évaluation — {datetime.now():%Y-%m-%d %H:%M}",
          "", f"Mode agent : **{lignes[0]['mode']}** · {len(lignes)} cas · "
          f"**{total_ok}/{len(lignes)} réussis ({100 * total_ok // len(lignes)} %)**", "",
          "| Catégorie | Réussis | Total |", "|---|---|---|"]
    for cat, oks in cats.items():
        md.append(f"| {cat} | {sum(oks)} | {len(oks)} |")
    md += ["", f"Latence : mediane {statistics.median(latences):.0f} ms · "
           f"max {max(latences)} ms (mesuree de bout en bout, traces JSONL dans traces/).", "",
           "Cas en échec :" if total_ok < len(lignes) else "Aucun cas en échec."]
    for l in lignes:
        if not l["reussi"]:
            md.append(f"- **{l['id']}** ({l['categorie']}) : {l['motifs_echec']}")
    (ICI / "RESULTATS.md").write_text("\n".join(md), encoding="utf-8")
    print(f"\n{total_ok}/{len(lignes)} reussis -> eval_results.csv, RESULTATS.md")


if __name__ == "__main__":
    main()
