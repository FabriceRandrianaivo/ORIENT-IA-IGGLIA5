"""Assemble le paquet de deploiement Hugging Face Spaces d'ORIENT'IA.

Usage :
    python deploy/build_space.py

Produit deploy/space/ : un dossier autonome pret a etre pousse dans un Space
(SDK Streamlit). Il copie uniquement ce dont l'application a besoin en
conservant l'arborescence (les chemins relatifs du code restent valables) :
    agent/  rag/  models/(train.py, model.joblib)  data/(formations.json, corpus/txt)
    requirements.txt allege + README.md avec l'en-tete YAML exige par HF.

Procedure de deploiement (une seule fois, ~10 min, gratuit) :
  1. Creer un compte sur https://huggingface.co (gratuit, pas de carte).
  2. New Space -> Nom : orientia -> SDK : Streamlit -> Public -> Create.
  3. Onglet "Files" -> "Add file" -> "Upload files" -> glisser TOUT le contenu
     de deploy/space/ (ou pousser par git avec un token d'acces).
  4. Le Space se construit (~3 min) puis l'app est en ligne a l'adresse
     https://huggingface.co/spaces/<votre-compte>/orientia
  Mise a jour : relancer ce script puis re-uploader les fichiers modifies.
"""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPACE = ROOT / "deploy" / "space"

README_HF = """---
title: ORIENT'IA
emoji: \U0001F393
colorFrom: green
colorTo: gray
sdk: streamlit
sdk_version: "1.40.0"
app_file: agent/app.py
pinned: false
---

# ORIENT'IA — Assistant d'orientation pedagogique ISPM

Prototype academique (examen de fin d'etudes Master 2). Les recommandations ne
remplacent ni l'avis d'un conseiller pedagogique ni une decision officielle
d'admission. Code source et documentation : depot GitHub du projet.
"""

REQUIREMENTS_SPACE = """streamlit>=1.40
pandas>=2.2
scikit-learn>=1.8,<1.9
joblib>=1.4
rank-bm25>=0.2
"""


def copier(rel: str):
    src, dst = ROOT / rel, SPACE / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        shutil.copy2(src, dst)
    print(f"  + {rel}")


def main():
    if SPACE.exists():
        shutil.rmtree(SPACE)
    SPACE.mkdir(parents=True)

    for rel in ["agent/agent.py", "agent/app.py", "agent/tools.py", "agent/prompts.py",
                "agent/graph.json", "rag/moteur.py",
                "models/train.py", "models/model.joblib",
                "data/formations.json", "data/corpus/txt"]:
        copier(rel)

    (SPACE / "README.md").write_text(README_HF, encoding="utf-8")
    (SPACE / "requirements.txt").write_text(REQUIREMENTS_SPACE, encoding="utf-8")
    (SPACE / "traces" / ".gitkeep").parent.mkdir(exist_ok=True)
    (SPACE / "traces" / ".gitkeep").write_text("", encoding="utf-8")
    print(f"\n[OK] Paquet pret : {SPACE}")
    print("Suivre la procedure en tete de ce script pour le mettre en ligne.")


if __name__ == "__main__":
    main()
