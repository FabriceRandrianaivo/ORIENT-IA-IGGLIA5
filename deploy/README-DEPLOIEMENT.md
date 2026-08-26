# Déploiement web d'ORIENT'IA — options gratuites

L'application fonctionne d'abord **en local** (`streamlit run agent/app.py`) : c'est le mode
de la démonstration au jury, sans dépendance réseau. Le déploiement web sert au test
partagé par l'équipe et aux correcteurs.

## Option 1 (recommandée) — Render, branché sur le repo GitHub

Gratuit, sans carte bancaire, jamais archivé. L'app s'endort après 15 min d'inactivité
et **se réveille seule en ~1 min** quand on ouvre le lien (pas besoin de cron).

1. Créer un compte sur https://render.com avec le compte GitHub du propriétaire du repo.
2. Dashboard → **New → Blueprint** → sélectionner le repo `ORIENT-IA-IGGLIA5`.
   Render lit automatiquement le fichier `render.yaml` à la racine (service `orientia`,
   branche `develop`).
   — ou bien : New → Web Service → repo → Runtime Python → coller les commandes de
   `render.yaml` à la main.
3. Deploy. Premier build ~5 min. URL du type `https://orientia.onrender.com`.
4. Chaque `git push` sur `develop` redéploie automatiquement — l'équipe teste toujours
   la dernière version.

Limites du plan gratuit : 512 Mo de RAM (suffisant pour notre app), mise en veille
15 min (réveil automatique ~1 min — prévenir les correcteurs que le premier
chargement peut prendre une minute).

## Option 2 (secours immédiat) — tunnel depuis un PC de l'équipe

Sans aucun compte cloud : on expose le Streamlit local via un tunnel gratuit.

1. `streamlit run agent/app.py` sur un PC de l'équipe.
2. Télécharger cloudflared (gratuit, sans compte) :
   https://github.com/cloudflare/cloudflared/releases
3. `cloudflared tunnel --url http://localhost:8501`
   → donne une URL publique `https://xxxx.trycloudflare.com` à partager.

Limite : l'URL vit tant que le PC et le tunnel tournent (parfait pour une session de
test d'équipe, pas pour laisser aux correcteurs).

## Option 3 — Hugging Face Spaces (si l'équipe change d'avis)

Paquet prêt : `python deploy/build_space.py` puis suivre les instructions en tête du
script. Réveil automatique ~30 s, jamais archivé.

## Ce qu'on ne refera pas

Streamlit Community Cloud (streamlit.app) : les apps gratuites y sont archivées après
inactivité (vécu sur un projet précédent) — exclu pour cet examen.
