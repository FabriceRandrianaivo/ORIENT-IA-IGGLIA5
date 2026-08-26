"""Entrainement et comparaison des modeles d'orientation ORIENT'IA.

Usage :
    python models/train.py [--data data/synthetic/dataset.csv] [--seed 42]

Demarche (exigences du sujet, section 7) :
  - modele de reference simple (classe majoritaire) ;
  - comparaison d'au moins deux approches (regression logistique vs foret aleatoire) ;
  - metriques adaptees au classement top-k : top-1, top-3, F1 macro, MRR,
    calibration (ECE), matrice de confusion ;
  - test de stabilite : une petite perturbation du profil ne doit pas
    bouleverser le top-3 ;
  - split stratifie 80/20 sur le synthetique = validation interne.
    Le VRAI test de generalisation (transfert vers les reponses d'enquete
    reelles) est fait par transfert_reel.py une fois l'enquete gelee.

Sorties :
    models/model.joblib            meilleur modele + colonnes + classes
    models/metrics.json            toutes les metriques mesurees
    models/confusion_matrix.csv    matrice de confusion du meilleur modele
    models/RAPPORT-ML.md           rapport lisible pour le jury
"""

import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, f1_score
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parent
NOTES = ["note_maths", "note_sciences", "note_langues", "note_eco"]
MULTI = [("matieres_preferees", "mat"), ("competences", "comp"),
         ("interets", "int"), ("metiers_vises", "met")]


# ------------------------------------------------------------------ features
def build_features(df: pd.DataFrame) -> pd.DataFrame:
    X = df[NOTES].astype(float).copy()
    X = pd.concat([X,
                   pd.get_dummies(df["serie_bac"], prefix="serie"),
                   pd.get_dummies(df["environnement"], prefix="env")], axis=1)
    for col, pref in MULTI:
        mh = df[col].str.get_dummies(sep="|")
        mh.columns = [f"{pref}::{c}" for c in mh.columns]
        X = pd.concat([X, mh], axis=1)
    return X.astype(float)


def align(X: pd.DataFrame, columns) -> pd.DataFrame:
    """Aligne un jeu de features sur les colonnes vues a l'entrainement."""
    return X.reindex(columns=columns, fill_value=0.0)


# ------------------------------------------------------------------ metriques
def evaluate(model, X, y, classes) -> dict:
    proba = model.predict_proba(X)
    order = np.argsort(-proba, axis=1)
    idx_true = np.array([list(classes).index(v) for v in y])
    rank = np.argmax(order == idx_true[:, None], axis=1) + 1

    top1 = float(np.mean(rank == 1))
    top3 = float(np.mean(rank <= 3))
    mrr = float(np.mean(1.0 / rank))
    f1m = float(f1_score(y, model.predict(X), average="macro"))

    # Calibration : ECE a 10 bacs sur la probabilite max.
    conf = proba.max(axis=1)
    correct = (rank == 1).astype(float)
    ece, bords = 0.0, np.linspace(0, 1, 11)
    for lo, hi in zip(bords[:-1], bords[1:]):
        masque = (conf > lo) & (conf <= hi)
        if masque.sum():
            ece += abs(correct[masque].mean() - conf[masque].mean()) * masque.mean()

    return {"top1_accuracy": round(top1, 4), "top3_accuracy": round(top3, 4),
            "mrr": round(mrr, 4), "f1_macro": round(f1m, 4), "ece": round(float(ece), 4)}


def stabilite_top3(model, columns, df, classes, rng, n=300) -> float:
    """Perturbation minime (retrait d'un interet) -> recouvrement moyen du top-3."""
    ech = df.sample(min(n, len(df)), random_state=rng)
    base = ech.copy()
    pert = ech.copy()
    retenus = []
    for i, val in pert["interets"].items():
        parts = val.split("|")
        if len(parts) >= 2:
            parts = parts[1:]  # retire le premier interet
            retenus.append(i)
        pert.at[i, "interets"] = "|".join(parts)
    if not retenus:
        return 1.0
    base, pert = base.loc[retenus], pert.loc[retenus]
    p1 = model.predict_proba(align(build_features(base), columns))
    p2 = model.predict_proba(align(build_features(pert), columns))
    t1 = np.argsort(-p1, axis=1)[:, :3]
    t2 = np.argsort(-p2, axis=1)[:, :3]
    overlap = [len(set(a) & set(b)) / 3 for a, b in zip(t1, t2)]
    return round(float(np.mean(overlap)), 4)


# ------------------------------------------------------------------ pipeline
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=str(ROOT.parent / "data" / "synthetic" / "dataset.csv"))
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    df = pd.read_csv(args.data)
    y = df["filiere"]
    X = build_features(df)
    columns = list(X.columns)

    X_tr, X_va, y_tr, y_va, df_tr, df_va = train_test_split(
        X, y, df, test_size=0.2, stratify=y, random_state=args.seed)

    modeles = {
        "baseline_majoritaire": DummyClassifier(strategy="most_frequent"),
        "regression_logistique": LogisticRegression(max_iter=3000, class_weight="balanced"),
        "foret_aleatoire": RandomForestClassifier(
            n_estimators=400, class_weight="balanced", random_state=args.seed, n_jobs=-1),
    }

    resultats = {}
    for nom, modele in modeles.items():
        modele.fit(X_tr, y_tr)
        resultats[nom] = evaluate(modele, X_va, y_va, modele.classes_)
        print(f"{nom:24s} {resultats[nom]}")

    # Meilleur modele = meilleur top-3 (metrique metier : on propose un top-3).
    best_nom = max((n for n in resultats if n != "baseline_majoritaire"),
                   key=lambda n: resultats[n]["top3_accuracy"])
    best = modeles[best_nom]
    print(f"\nMeilleur modele : {best_nom}")

    stab = stabilite_top3(best, columns, df_va, best.classes_, args.seed)
    resultats[best_nom]["stabilite_top3"] = stab
    print(f"Stabilite du top-3 sous perturbation : {stab}")

    # Matrice de confusion + pires classes -> analyse des erreurs.
    cm = confusion_matrix(y_va, best.predict(X_va), labels=best.classes_)
    pd.DataFrame(cm, index=best.classes_, columns=best.classes_).to_csv(ROOT / "confusion_matrix.csv")
    f1_classes = f1_score(y_va, best.predict(X_va), average=None, labels=best.classes_)
    pires = sorted(zip(best.classes_, f1_classes), key=lambda t: t[1])[:4]

    # Importances de variables (pour expliquer_recommandation).
    importances = {}
    if hasattr(best, "feature_importances_"):
        top = np.argsort(-best.feature_importances_)[:15]
        importances = {columns[i]: round(float(best.feature_importances_[i]), 4) for i in top}

    joblib.dump({"model": best, "columns": columns, "classes": list(best.classes_),
                 "nom": best_nom, "seed": args.seed}, ROOT / "model.joblib")

    metrics = {"seed": args.seed, "n_total": len(df), "n_train": len(X_tr), "n_validation": len(X_va),
               "split": "80/20 stratifie sur donnees synthetiques (validation interne ; "
                        "le test reel = reponses d'enquete, voir transfert_reel.py)",
               "modeles": resultats, "meilleur_modele": best_nom,
               "pires_classes_f1": {c: round(float(v), 4) for c, v in pires},
               "importances_top15": importances}
    (ROOT / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")

    # Rapport lisible.
    lignes = ["# Rapport ML — ORIENT'IA", "",
              f"Jeu : {len(df)} profils synthetiques · split 80/20 stratifie · seed {args.seed}.",
              "La validation ci-dessous est INTERNE (synthetique -> synthetique).",
              "Le test de generalisation vers les profils reels est produit par `transfert_reel.py`",
              "apres le gel de l'enquete.", "",
              "| Modele | Top-1 | Top-3 | MRR | F1 macro | ECE |", "|---|---|---|---|---|---|"]
    for nom, r in resultats.items():
        lignes.append(f"| {nom} | {r['top1_accuracy']} | {r['top3_accuracy']} | "
                      f"{r['mrr']} | {r['f1_macro']} | {r['ece']} |")
    lignes += ["", f"**Meilleur modele : {best_nom}** (selection sur le top-3, metrique metier).",
               f"Stabilite du top-3 sous retrait d'un interet : **{stab}**.", "",
               "## Classes les plus difficiles (F1 par classe)",
               "", *[f"- {c} : {v:.3f}" for c, v in pires], "",
               "## Importances de variables (top 15)", "",
               *[f"- {k} : {v}" for k, v in importances.items()], "",
               "La matrice de confusion complete est dans `confusion_matrix.csv`."]
    (ROOT / "RAPPORT-ML.md").write_text("\n".join(lignes), encoding="utf-8")
    print(f"\n[OK] model.joblib, metrics.json, confusion_matrix.csv, RAPPORT-ML.md -> {ROOT}")


if __name__ == "__main__":
    main()
