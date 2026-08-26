"""Genere le schema d'architecture d'ORIENT'IA (livrable 11).

Usage : python docs/generer_schema.py  ->  docs/architecture.png
Reproductible : le schema est du code, pas un dessin manuel.
"""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

VERT, VERT_F, ORANGE, GRIS = "#1e6b45", "#e8f2ec", "#a85d1c", "#5b6459"


def boite(ax, x, y, w, h, titre, sous, couleur=VERT, fond=VERT_F):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012",
                                facecolor=fond, edgecolor=couleur, linewidth=1.6))
    ax.text(x + w / 2, y + h * 0.62, titre, ha="center", va="center",
            fontsize=10.5, fontweight="bold", color="#20261f")
    ax.text(x + w / 2, y + h * 0.28, sous, ha="center", va="center",
            fontsize=8, color=GRIS)


def fleche(ax, x1, y1, x2, y2, couleur=VERT, style="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=14, linewidth=1.5,
                                 linestyle=style, color=couleur))


def main():
    fig, ax = plt.subplots(figsize=(12, 7.5))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 9)
    ax.axis("off")
    ax.text(6, 8.65, "ORIENT'IA — Architecture", ha="center",
            fontsize=15, fontweight="bold", color=VERT)
    ax.text(6, 8.25, "Deux chaînes d'acquisition convergeant vers un agent unique, chaque décision traçable",
            ha="center", fontsize=9, color=GRIS)

    # Chaine documentaire (gauche)
    boite(ax, 0.4, 6.7, 3.2, 1.1, "Sources ISPM", "site officiel · brochure PDF\n(scrape_ispm.py)")
    boite(ax, 0.4, 5.0, 3.2, 1.1, "Corpus structuré", "formations.json · corpus txt\n+ registre des sources")
    boite(ax, 0.4, 3.3, 3.2, 1.1, "Index hybride", "BM25 + TF-IDF · citations [src-…]")
    fleche(ax, 2.0, 6.7, 2.0, 6.1)
    fleche(ax, 2.0, 5.0, 2.0, 4.4)

    # Chaine ML (droite)
    boite(ax, 8.4, 6.7, 3.2, 1.1, "Profils synthétiques", "3 000 · règles documentées\n(entraînement)")
    boite(ax, 4.4, 6.7, 3.2, 1.1, "Enquête réelle", "consentement · anonymisée\n(validation / test)")
    boite(ax, 8.4, 5.0, 3.2, 1.1, "Jeu de données", "vocabulaire commun\nsynthétique + réel")
    boite(ax, 8.4, 3.3, 3.2, 1.1, "Modèle ML", "rég. logistique · top-3 0,83\ncalibration ECE 0,07")
    fleche(ax, 10.0, 6.7, 10.0, 6.1)
    fleche(ax, 6.0, 6.7, 8.9, 6.05)
    fleche(ax, 10.0, 5.0, 10.0, 4.4)

    # Agent (centre)
    boite(ax, 3.9, 1.6, 4.2, 1.4, "AGENT CONVERSATIONNEL",
          "5 outils · graphe 115 arêtes · refus sécurité\n3 modes : déterministe / Gemini / Anthropic")
    fleche(ax, 3.6, 3.5, 4.6, 3.0)
    fleche(ax, 8.4, 3.5, 7.4, 3.0)

    # Sortie + traces
    boite(ax, 3.9, 0.15, 4.2, 1.0, "Recommandation argumentée",
          "sources citées · incertitude déclarée · mention obligatoire")
    fleche(ax, 6.0, 1.6, 6.0, 1.15)
    boite(ax, 9.0, 1.0, 2.6, 1.2, "Traces JSONL", "question · profil · outils\nscores · latence · refus",
          couleur=ORANGE, fond="#f8efe4")
    fleche(ax, 8.1, 2.0, 9.0, 1.8, couleur=ORANGE, style="--")

    out = Path(__file__).with_name("architecture.png")
    fig.savefig(out, dpi=160, bbox_inches="tight", facecolor="white")
    print(f"[OK] {out}")


if __name__ == "__main__":
    main()
