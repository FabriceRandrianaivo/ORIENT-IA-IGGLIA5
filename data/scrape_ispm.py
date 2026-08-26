"""Collecte reproductible du corpus pedagogique depuis le site officiel de l'ISPM.

Usage :
    python data/scrape_ispm.py

Sorties :
    data/corpus/raw/<page>.html   HTML brut tel que telecharge (preuve de collecte)
    data/corpus/txt/<page>.txt    Texte extrait, pret pour le decoupage RAG
    data/registre_sources.csv     Registre des sources (exigence du sujet, section 4)

Le site declare charset=utf-8 mais sert en realite du Windows-1252 : on tente
utf-8 strict puis on retombe sur cp1252, sinon les accents sont perdus.
"""

import csv
import html
import re
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

BASE = "https://ispm-edu.com/"
UA = {"User-Agent": "Mozilla/5.0 (corpus academique ORIENT'IA - examen ISPM M2)"}

# Pages retenues : celles qui portent l'information pedagogique utile a
# l'orientation. Les pages vie du campus / photos / annuaires sont exclues.
PAGES = {
    "accueil": ("index.php", "Page d'accueil du site officiel"),
    "presentation": ("presentation.php", "Presentation generale de l'institut"),
    "filieres": ("filieres.php", "Departements et filieres : liste officielle des 16 filieres avec sigles et descriptions"),
    "inscription": ("inscription.php", "Modalites et conditions d'inscription"),
}

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "corpus" / "raw"
TXT = ROOT / "corpus" / "txt"
REGISTRE = ROOT / "registre_sources.csv"


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def decode(body: bytes) -> str:
    """Le site melange UTF-8 et Windows-1252 dans une meme page (includes PHP
    d'encodages differents). On decode en cp1252 puis on repare ligne par ligne
    les sequences UTF-8 doublement encodees (ex. 'Ã©' -> 'e accentue')."""
    text = body.decode("cp1252", errors="replace")
    repaired = []
    for line in text.split("\n"):
        if "Ã" in line or "â€" in line:
            try:
                line = line.encode("cp1252").decode("utf-8")
            except (UnicodeEncodeError, UnicodeDecodeError):
                pass
        repaired.append(line)
    return "\n".join(repaired)


def to_text(page_html: str) -> str:
    """Extraction de texte volontairement simple et sans dependance externe."""
    page_html = re.sub(r"<script.*?</script>", " ", page_html, flags=re.S | re.I)
    page_html = re.sub(r"<style.*?</style>", " ", page_html, flags=re.S | re.I)
    page_html = re.sub(r"<!--.*?-->", " ", page_html, flags=re.S)
    text = re.sub(r"<[^>]+>", "\n", page_html)
    text = html.unescape(text)
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return "\n".join(lines)


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    TXT.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    registre_rows = []

    for slug, (path, description) in PAGES.items():
        url = BASE + path
        try:
            body = fetch(url)
        except (urllib.error.URLError, OSError) as exc:
            print(f"[ECHEC] {url} : {exc}")
            registre_rows.append([f"src-{slug}", description, url, today, "officiel",
                                  "aucune (echec de telechargement)", f"echec : {exc}"])
            continue
        page = decode(body)
        (RAW / f"{slug}.html").write_text(page, encoding="utf-8")
        (TXT / f"{slug}.txt").write_text(to_text(page), encoding="utf-8")
        print(f"[OK] {url} -> corpus/raw/{slug}.html ({len(body)} octets)")
        registre_rows.append([f"src-{slug}", description, url, today, "officiel",
                              "texte integral de la page",
                              "site institutionnel ; date de mise a jour du contenu inconnue"])

    # La brochure est referencee dans le HTML (lien commente) : on tente.
    url = BASE + "download.php?file=brochure"
    try:
        body = fetch(url)
        if body[:4] == b"%PDF":
            (RAW / "brochure.pdf").write_bytes(body)
            print(f"[OK] brochure PDF ({len(body)} octets)")
            registre_rows.append(["src-brochure", "Brochure officielle des filieres", url,
                                  today, "officiel", "document PDF integral (departements, cursus et diplomes, taux d'embauche)",
                                  "lien desactive sur le site mais fichier encore servi ; document non date, "
                                  "prix listes jusqu'en 2009 -> contenu potentiellement obsolete ; mentionne un "
                                  "'concours d'entree' la ou inscription.php decrit une 'selection de dossier' "
                                  "(contradiction a signaler par l'assistant)"])
        else:
            print("[INFO] download.php?file=brochure ne renvoie pas un PDF, ignore")
    except (urllib.error.URLError, OSError) as exc:
        print(f"[INFO] brochure indisponible : {exc}")

    # Source hors-ligne : brochure papier fournie par l'equipe (transcrite dans
    # corpus/txt/brochure-papier.txt). Plus recente que le site (mentionne 2025).
    registre_rows.append(["src-brochure-papier",
                          "Brochure officielle ISPM (edition papier, posterieure a 2025)",
                          "document imprime fourni par l'equipe (pas d'URL)", "2026-08-26",
                          "officiel",
                          "mentions et parcours (structure LMD, 6 mentions), mode d'admission "
                          "(dossier + entretien eventuel), pieces et frais L1 (40.000 Ar) et "
                          "transferts L2/L3/M1 (60.000 Ar), conditions de bac par mention, "
                          "historique (LMD 2015, Licence et Master), infrastructures, publications",
                          "transcription manuelle (coquilles OCR possibles) ; contredit le site sur "
                          "les frais (30.000 Ar sur inscription.php) et precise le mode d'admission ; "
                          "etant plus recente, elle fait foi avec reserve — a confirmer aupres de "
                          "l'administration"])

    with REGISTRE.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["id", "titre", "origine_url", "date_consultation",
                         "statut", "donnees_extraites", "limites"])
        writer.writerows(registre_rows)
    print(f"[OK] registre -> {REGISTRE}")


if __name__ == "__main__":
    main()
