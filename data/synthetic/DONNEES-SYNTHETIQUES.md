# Données synthétiques — méthode, hypothèses, biais et contrôles

Documentation exigée par le sujet (section 5) pour le jeu `dataset.csv` produit par `generateur.py`.

## Méthode de génération

1. **Profil d'abord, étiquette ensuite.** On génère un profil réaliste (série de bac, notes 1–5 sur 4 domaines, matières préférées, compétences, centres d'intérêt, environnement de travail, métiers visés), puis on calcule un score d'affinité pour chacune des 16 filières de l'ISPM et on tire l'étiquette.
2. **Corrélations internes du profil** : les matières préférées sont tirées avec un poids proportionnel aux notes (« on préfère ce où l'on est bon ») ; les compétences et intérêts sont biaisés vers les matières préférées (ex. Informatique → Programmation) avec une part de hasard.
3. **Filtre d'éligibilité officiel** : seules les filières dont la condition de série de bac est satisfaite peuvent être tirées (source : page inscription du site ISPM, voir `../registre_sources.csv`, y compris la règle « A2 avec maths ≥ 12 » pour la biotechnologie, traduite en note ≥ 3/5).
4. **Bruit d'étiquette volontaire** : l'étiquette est tirée par softmax des scores (température 1,2), pas par argmax. Deux profils identiques peuvent donc choisir des filières différentes, comme dans la réalité. Le modèle ne peut pas atteindre 100 % : c'est voulu.
5. **Reproductibilité** : graine fixée (`--seed 42`), 3 000 profils par défaut.

## Alignement avec l'enquête

Le vocabulaire de chaque champ est identique à celui du questionnaire (`ENQUETE-QUESTIONNAIRES.md`), afin que le modèle entraîné sur le synthétique soit directement évaluable sur les réponses réelles (montage recommandé par le sujet : synthétique = entraînement, enquête = validation/test).

## Hypothèses assumées

- La répartition des séries de bac (D et S majoritaires, techniques minoritaires) est une estimation d'équipe, non une statistique officielle.
- Les règles d'affinité filière ↔ profil (matrice `AFFINITES`) reflètent le contenu des descriptions officielles des filières, complété par le bon sens de l'équipe. Elles n'ont pas de validité statistique établie.
- Les notes sont corrélées à la série de bac (maths plus élevées en C/S, langues en A/L), avec bruit gaussien.
- Le sexe et l'âge ne sont **pas générés** : choix délibéré pour qu'aucun modèle entraîné sur ces données ne puisse utiliser ces attributs.

## Biais potentiellement introduits

- **Biais de règles** : le modèle qui apprend ce jeu retrouve principalement nos règles d'affinité (limite nommée par le sujet lui-même). D'où la validation sur données d'enquête réelles.
- **Déséquilibre de classes** : la distribution obtenue va de CAA (~14 %) à IAA (~1,6 %). IAA est une classe rare : à traiter à l'entraînement (pondération de classes) et à commenter dans l'analyse d'erreurs.
- **Corrélations simplistes** : les mappings matière→compétence et matière→intérêt sont plus nets que dans la réalité ; le modèle peut sur-apprendre ces raccourcis.
- **Vocabulaire fermé** : les profils réels s'expriment plus librement (champ « Autre » de l'enquête) ; un recodage sera nécessaire et sera documenté dans le registre de collecte.

## Contrôles de cohérence appliqués

- Aucun profil n'est étiqueté vers une filière dont il ne satisfait pas la condition de série de bac (contrôle structurel : le filtre d'éligibilité est appliqué avant le tirage).
- Notes bornées 1–5 ; nombre de matières préférées (2–3), compétences (2–4), intérêts (2–4) bornés comme dans le questionnaire.
- Tirages sans remise : pas de doublon dans les listes d'un même profil.
- La répartition des étiquettes est affichée à chaque exécution ; toute classe < 2 % est signalée par le script.
