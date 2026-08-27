"""Genere le schema du traitement d'une requete utilisateur (support de soutenance).

Usage : python docs/generer_schema_requete.py  ->  docs/flux_requete.png
"""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

VERT, VERT_F = "#1e6b45", "#e8f2ec"
ORANGE, ORANGE_F = "#a85d1c", "#f8efe4"
ROUGE, ROUGE_F = "#a83232", "#f6e7e7"
BLEU, BLEU_F = "#2c5f8a", "#e8eff5"
GRIS = "#5b6459"


def boite(ax, x, y, w, h, titre, sous="", couleur=VERT, fond=VERT_F, fs=9.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012",
                                facecolor=fond, edgecolor=couleur, linewidth=1.5))
    if sous:
        ax.text(x + w / 2, y + h * 0.66, titre, ha="center", va="center",
                fontsize=fs, fontweight="bold", color="#20261f")
        ax.text(x + w / 2, y + h * 0.30, sous, ha="center", va="center",
                fontsize=7.2, color=GRIS, family="monospace")
    else:
        ax.text(x + w / 2, y + h / 2, titre, ha="center", va="center",
                fontsize=fs, fontweight="bold", color="#20261f")


def fleche(ax, x1, y1, x2, y2, couleur=VERT, style="-", lw=1.6):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=13, linewidth=lw,
                                 linestyle=style, color=couleur))


def etiquette(ax, x, y, texte, couleur=GRIS):
    ax.text(x, y, texte, fontsize=7.5, color=couleur, ha="left", va="center",
            fontstyle="italic")


def main():
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 12.4)
    ax.axis("off")

    ax.text(7, 12.1, "ORIENT'IA — Traitement d'une requête utilisateur",
            ha="center", fontsize=15, fontweight="bold", color=VERT)
    ax.text(7, 11.72, "De la question à la réponse : phases, fonctions et garanties",
            ha="center", fontsize=9, color=GRIS)

    X, W = 4.0, 6.0  # colonne centrale

    # 0. Entree
    boite(ax, X, 10.7, W, 0.75, "Question + profil déclaré",
          "interface Streamlit — app.py : traiter()", couleur=BLEU, fond=BLEU_F)
    fleche(ax, 7, 10.7, 7, 10.35)

    # 1. Point d'entree
    boite(ax, X, 9.6, W, 0.75, "1 · Point d'entrée unique",
          "agent.py : repondre(question, profil)")
    fleche(ax, 7, 9.6, 7, 9.25)

    # 2. Securite
    boite(ax, X, 8.5, W, 0.75, "2 · Barrage de sécurité (avant tout)",
          "_detecter_refus() : injection · discrimination · profilage")
    boite(ax, 10.6, 8.5, 3.1, 0.75, "REFUS motivé",
          "réponse directe, tracée", couleur=ROUGE, fond=ROUGE_F, fs=8.5)
    fleche(ax, 10.0, 8.87, 10.6, 8.87, couleur=ROUGE)
    fleche(ax, 7, 8.5, 7, 8.15)

    # 3. Choix moteur
    boite(ax, X, 7.4, W, 0.75, "3 · Choix du moteur (.env)",
          "Anthropic > Gemini > Groq > déterministe")
    fleche(ax, 7, 7.4, 7, 7.05)

    # 4. Routeur
    boite(ax, X, 6.3, W, 0.75, "4 · Routeur d'intentions",
          "_mode_deterministe() : normalisation + cascade de motifs")
    # intents (2 rangees de 3 sous le routeur, a gauche)
    intents = [("Liste des filières", "6 mentions · 16 parcours"),
               ("Institutionnel", "fiche établissement"),
               ("Clarification", "profil incomplet / vague"),
               ("Comparaison", "comparer_parcours()"),
               ("Prérequis", "verifier_prerequis()"),
               ("Recommandation", "analyser_profil_ml()")]
    for i, (t, s) in enumerate(intents):
        bx = 0.25 + (i % 2) * 1.85
        by = 5.55 - (i // 2) * 0.72
        boite(ax, bx, by, 1.75, 0.58, t, s, fs=7.3)
    ax.add_patch(FancyBboxPatch((0.15, 3.95), 3.9, 2.35, boxstyle="round,pad=0.02",
                                facecolor="none", edgecolor=GRIS, linewidth=0.8,
                                linestyle="--"))
    etiquette(ax, 0.25, 3.8, "branches du routeur (la 1re qui matche répond)")
    fleche(ax, 4.6, 6.3, 3.4, 6.15, couleur=GRIS, style="--", lw=1.1)
    fleche(ax, 7, 6.3, 7, 5.95)

    # 5. Outils
    boite(ax, X, 4.85, W, 1.1, "5 · Outils (tools.py) — le vrai travail",
          "rechercher_formation() BM25+TF-IDF+synonymes · analyser_profil_ml()\n"
          "model.joblib top-3 · verifier_prerequis() règles · chemins_graphe() 115 arêtes")
    boite(ax, 10.6, 4.95, 3.1, 0.9, "Corpus + modèle",
          "formations.json · corpus/txt\nregistre des sources", couleur=ORANGE,
          fond=ORANGE_F, fs=8.5)
    fleche(ax, 10.6, 5.4, 10.0, 5.4, couleur=ORANGE, style="--", lw=1.1)
    fleche(ax, 7, 4.85, 7, 4.5)

    # 6. Garanties
    boite(ax, X, 3.4, W, 1.05, "6 · Garanties de fiabilité",
          "_pertinent() filtre les passages · fiche du sigle toujours injectée\n"
          "rien de pertinent -> aveu honnête + renvoi administration")
    fleche(ax, 7, 3.4, 7, 3.05)

    # 7. Reformulation LLM
    boite(ax, X, 1.95, W, 1.05, "7 · Reformulation LLM (optionnelle)",
          "_mode_gemini() -> _mode_groq() en secours -> brouillon si quotas épuisés\n"
          "le LLM reformule, il ne peut PAS ajouter de faits")
    fleche(ax, 7, 1.95, 7, 1.6)

    # 8. Sortie
    boite(ax, X, 0.55, W, 1.0, "8 · Trace + réponse",
          "_tracer() JSONL : question, profil, outils, scores, latence, refus\n"
          "UI : cartes top-3 · sources citées · traces · questions suivantes",
          couleur=BLEU, fond=BLEU_F)
    boite(ax, 10.6, 0.65, 3.1, 0.8, "traces/*.jsonl",
          "observabilité complète", couleur=ORANGE, fond=ORANGE_F, fs=8.5)
    fleche(ax, 10.0, 1.05, 10.6, 1.05, couleur=ORANGE, style="--", lw=1.1)

    out = Path(__file__).with_name("flux_requete.png")
    fig.savefig(out, dpi=160, bbox_inches="tight", facecolor="white")
    print(f"[OK] {out}")


if __name__ == "__main__":
    main()
