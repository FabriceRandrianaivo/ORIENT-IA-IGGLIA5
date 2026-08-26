"""Mesure du transfert : modele entraine sur le synthetique, teste sur l'enquete reelle.

C'est LA mesure mise en avant par le sujet : la capacite du modele a generaliser
de profils generes vers des profils declares par de vraies personnes.

Usage (apres gel de l'enquete et recodage au format du dataset synthetique) :
    python models/transfert_reel.py --data data/enquete/reponses_recodees.csv

Le fichier d'entree doit avoir les memes colonnes que data/synthetic/dataset.csv
(serie_bac, note_*, matieres_preferees, competences, interets, environnement,
metiers_vises, filiere). Le recodage des reponses libres est documente dans le
registre de collecte.
"""

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd

from train import align, build_features, evaluate

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=str(ROOT.parent / "data" / "enquete" / "reponses_recodees.csv"))
    parser.add_argument("--population", default=None,
                        help="Filtre optionnel sur une colonne 'population' (etudiant / professionnel)")
    args = parser.parse_args()

    bundle = joblib.load(ROOT / "model.joblib")
    model, columns = bundle["model"], bundle["columns"]

    df = pd.read_csv(args.data)
    if args.population and "population" in df.columns:
        df = df[df["population"] == args.population]
    if df.empty:
        raise SystemExit("Aucune ligne a evaluer : verifier le fichier ou le filtre.")

    X = align(build_features(df), columns)
    res = evaluate(model, X, df["filiere"], model.classes_)
    res["n_reponses"] = len(df)
    res["avertissement"] = ("Echantillon reel petit et auto-selectionne : intervalles de "
                            "confiance larges, a annoncer comme tels (cf. sujet).")

    print(f"Transfert synthetique -> reel ({len(df)} reponses"
          + (f", population={args.population}" if args.population else "") + ") :")
    for k, v in res.items():
        print(f"  {k}: {v}")

    out = ROOT / "metrics_transfert_reel.json"
    existant = json.loads(out.read_text(encoding="utf-8")) if out.exists() else {}
    existant[args.population or "toutes_populations"] = res
    out.write_text(json.dumps(existant, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[OK] -> {out}")


if __name__ == "__main__":
    main()
