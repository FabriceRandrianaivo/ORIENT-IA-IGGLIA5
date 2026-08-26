# Apport démontré de l'IA symbolique (graphe + règles officielles)

Exigence du sujet (§12) : « son apport devra être démontré pour être valorisé ».
Trois démonstrations, dont une mesurée sur 300 profils.

## 1. Correction des recommandations du ML (mesuré)

Sur 300 profils synthétiques tirés au hasard (seed 42), le **top-1 du modèle
statistique viole les conditions officielles de série de bac dans 2.3 % des cas**
(7 profils). Sans la couche symbolique, ces recommandations partiraient
telles quelles ; avec elle, l'incohérence est détectée (`verifier_prerequis` /
`calculer_score_adequation`) et l'assistant signale le conflit — comportement exigé
par la question type du jury « que fais-tu si le modèle ML et les règles se
contredisent ? ».

Exemples corrigés :
  - syn-00289 (bac Technique genie civil) : top-1 ML = PIP, prerequis non remplis
  - syn-00521 (bac A1) : top-1 ML = ESIIA, prerequis non remplis
  - syn-01830 (bac A1) : top-1 ML = IMTICIA, prerequis non remplis
  - syn-00978 (bac L) : top-1 ML = PIP, prerequis non remplis
  - syn-01732 (bac A2) : top-1 ML = AEE, prerequis non remplis

## 2. Raisonnement multi-étape explicatif

Un candidat qui prefere les Mathematiques -> ISAIA enseigne Mathématiques, Statistique appliquée, Informatique -> prepare aux debouches : Banques, Entreprises industrielles, Entreprises commerciales. Chemin en 2 sauts produit par le graphe, avec source [src-filieres] ; le modele statistique seul ne renvoie qu'une probabilite sans chemin explicatif.

## 3. Vérification de prérequis fondée sur la règle citée

Bac A2, maths 2/5, filiere PIP -> eligible=False ; detail : Bac A2 avec maths < 12/20 : condition officielle non remplie. ; regle officielle citee : "Bacc C, D, S, Techniques agricoles et A2 avec note de mathématiques >= 12" [src-inscription]. Le ML seul aurait pu classer PIP en tete sans detecter l'ineligibilite.

## Conclusion

Le graphe (115 arêtes construites depuis `data/formations.json`, source officielle)
n'est pas décoratif : il **corrige** le modèle statistique (2.3 % des top-1 sur
l'échantillon), **explique** les recommandations par des chemins vérifiables, et
**fonde** les réponses réglementaires sur des règles citées. Ces trois usages sont
intégrés à l'agent via les outils `verifier_prerequis`, `chemins_graphe` et
`calculer_score_adequation`, et couverts par la campagne d'évaluation (32/32).
