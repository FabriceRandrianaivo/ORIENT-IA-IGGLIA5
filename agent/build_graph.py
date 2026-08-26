"""Construit le graphe de connaissances (extension IA symbolique du sujet).

Relations produites depuis data/formations.json (sources officielles) :
    Parcours appartientA  Departement
    Parcours enseigne     Matiere
    Parcours developpe    Competence
    Parcours prepareA     Metier
    Parcours necessite    Prerequis (serie de bac)

Usage : python agent/build_graph.py  ->  agent/graph.json
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    data = json.loads((ROOT / "data" / "formations.json").read_text(encoding="utf-8"))
    aretes = []
    for f in data["filieres"]:
        p = f["sigle"]
        aretes.append([p, "appartientA", f["departement"]])
        aretes.append([p, "necessite", f["prerequis_bac"]])
        for m in f.get("matieres_principales") or []:
            aretes.append([p, "enseigne", m])
        for c in f.get("competences_developpees") or []:
            aretes.append([p, "developpe", c])
        for d in f.get("debouches") or []:
            aretes.append([p, "prepareA", d])

    graphe = {"_source": "data/formations.json (voir registre_sources.csv)",
              "relations": ["appartientA", "necessite", "enseigne", "developpe", "prepareA"],
              "aretes": aretes}
    out = Path(__file__).with_name("graph.json")
    out.write_text(json.dumps(graphe, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"[OK] {len(aretes)} aretes -> {out}")


if __name__ == "__main__":
    main()
