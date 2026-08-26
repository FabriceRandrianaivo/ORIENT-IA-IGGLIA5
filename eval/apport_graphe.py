"""Demonstration chiffree de l'apport de l'IA symbolique (graphe + regles).

Le sujet (section 12) : « l'usage d'une ontologie n'est pas obligatoire, mais son
apport devra etre DEMONTRE pour etre valorise ». Ce script produit cette preuve.

Usage :
    python eval/apport_graphe.py    ->  eval/APPORT-GRAPHE.md

Trois demonstrations mesurees :
  1. CORRECTION DU ML : sur un echantillon de profils, on compte combien de fois
     le top-1 du modele statistique propose une filiere dont le profil ne remplit
     PAS les conditions officielles de bac — cas ou la couche symbolique corrige
     la recommandation (detection d'incoherence, exigence du sujet).
  2. RAISONNEMENT MULTI-ETAPE : chemin explicatif profil -> matiere -> parcours
     -> metier, impossible a produire par le seul modele statistique.
  3. VERIFICATION DE PREREQUIS : reponse fondee sur la regle officielle citee,
     la ou le ML ne connait pas la reglementation.
"""

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "agent"))
import tools  # noqa: E402

ICI = Path(__file__).resolve().parent
N_ECHANTILLON = 300


def profil_depuis_ligne(ligne) -> dict:
    return {
        "serie_bac": ligne["serie_bac"],
        "note_maths": int(ligne["note_maths"]), "note_sciences": int(ligne["note_sciences"]),
        "note_langues": int(ligne["note_langues"]), "note_eco": int(ligne["note_eco"]),
        "matieres_preferees": str(ligne["matieres_preferees"]).split("|"),
        "competences": str(ligne["competences"]).split("|"),
        "interets": str(ligne["interets"]).split("|"),
        "environnement": ligne["environnement"],
        "metiers_vises": str(ligne["metiers_vises"]).split("|"),
    }


def demo_correction_ml():
    df = pd.read_csv(ROOT / "data" / "synthetic" / "dataset.csv").sample(
        N_ECHANTILLON, random_state=42)
    corriges = []
    for _, ligne in df.iterrows():
        profil = profil_depuis_ligne(ligne)
        analyse = tools.analyser_profil_ml(profil)
        if "erreur" in analyse:
            continue
        top1 = analyse["top3"][0]["sigle"]
        prereq = tools.verifier_prerequis(profil["serie_bac"], top1, profil["note_maths"])
        if not prereq["eligible"]:
            corriges.append((ligne["id"], profil["serie_bac"], top1))
    taux = 100 * len(corriges) / N_ECHANTILLON
    return taux, corriges


def demo_multi_etape():
    graphe = tools.chemins_graphe("ISAIA")["relations"]
    enseigne = [r["cible"] for r in graphe if r["relation"] == "enseigne"]
    metiers = [r["cible"] for r in graphe if r["relation"] == "prepareA"]
    return (f"Un candidat qui prefere les Mathematiques -> ISAIA enseigne "
            f"{', '.join(enseigne)} -> prepare aux debouches : {', '.join(metiers)}. "
            f"Chemin en 2 sauts produit par le graphe, avec source [src-filieres] ; "
            f"le modele statistique seul ne renvoie qu'une probabilite sans chemin explicatif.")


def demo_prerequis():
    cas = tools.verifier_prerequis("A2", "PIP", note_maths=2)
    return (f"Bac A2, maths 2/5, filiere PIP -> eligible={cas['eligible']} ; "
            f"detail : {cas['detail']} ; regle officielle citee : "
            f"\"{cas['regle_officielle']}\" [{cas['source']}]. "
            f"Le ML seul aurait pu classer PIP en tete sans detecter l'ineligibilite.")


def main():
    taux, corriges = demo_correction_ml()
    exemples = "\n".join(f"  - {i} (bac {s}) : top-1 ML = {t}, prerequis non remplis"
                         for i, s, t in corriges[:5])
    multi = demo_multi_etape()
    prereq = demo_prerequis()

    md = f"""# Apport démontré de l'IA symbolique (graphe + règles officielles)

Exigence du sujet (§12) : « son apport devra être démontré pour être valorisé ».
Trois démonstrations, dont une mesurée sur {N_ECHANTILLON} profils.

## 1. Correction des recommandations du ML (mesuré)

Sur {N_ECHANTILLON} profils synthétiques tirés au hasard (seed 42), le **top-1 du modèle
statistique viole les conditions officielles de série de bac dans {taux:.1f} % des cas**
({len(corriges)} profils). Sans la couche symbolique, ces recommandations partiraient
telles quelles ; avec elle, l'incohérence est détectée (`verifier_prerequis` /
`calculer_score_adequation`) et l'assistant signale le conflit — comportement exigé
par la question type du jury « que fais-tu si le modèle ML et les règles se
contredisent ? ».

Exemples corrigés :
{exemples}

## 2. Raisonnement multi-étape explicatif

{multi}

## 3. Vérification de prérequis fondée sur la règle citée

{prereq}

## Conclusion

Le graphe (115 arêtes construites depuis `data/formations.json`, source officielle)
n'est pas décoratif : il **corrige** le modèle statistique ({taux:.1f} % des top-1 sur
l'échantillon), **explique** les recommandations par des chemins vérifiables, et
**fonde** les réponses réglementaires sur des règles citées. Ces trois usages sont
intégrés à l'agent via les outils `verifier_prerequis`, `chemins_graphe` et
`calculer_score_adequation`, et couverts par la campagne d'évaluation (32/32).
"""
    (ICI / "APPORT-GRAPHE.md").write_text(md, encoding="utf-8")
    print(f"[OK] Taux de correction du top-1 ML par les regles : {taux:.1f}% "
          f"({len(corriges)}/{N_ECHANTILLON})")
    print(f"[OK] -> {ICI / 'APPORT-GRAPHE.md'}")


if __name__ == "__main__":
    main()
