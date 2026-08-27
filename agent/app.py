"""Interface ORIENT'IA (Streamlit) — Plateforme d'Orientation multi-pages.

Lancement :  streamlit run agent/app.py
Pages : Mon Profil (chat + recommandation) · Mes Échanges (historique réel des
traces) · Parcours (feuille de route LMD officielle) · Ressources (registre des
sources) · Paramètres (thème). Toutes les données affichées sont réelles.
"""

import csv
import json
import re
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))
import agent  # noqa: E402
import tools  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

MATIERES = ["Mathematiques", "Physique-Chimie", "SVT", "Informatique / Technologie",
            "Francais / Litterature", "Langues etrangeres", "Histoire-Geographie",
            "Economie / Gestion", "Arts", "Sport"]
COMPETENCES = ["Programmation", "Analyse de donnees / logique", "Redaction / communication",
               "Creativite / design", "Organisation / gestion de projet", "Vente / negociation",
               "Electronique / bricolage technique", "Travail en equipe"]
INTERETS = ["Technologie / informatique", "Sciences", "Entrepreneuriat / business",
            "Finance / comptabilite", "Art / design / audiovisuel", "Communication / medias",
            "Tourisme / hotellerie", "Agriculture / environnement", "BTP / construction",
            "Sante / social", "Droit / justice"]
ENVIRONNEMENTS = ["", "Bureau", "Terrain / exterieur", "Laboratoire", "Atelier / usine", "Mixte"]
METIERS = ["Technique / ingenierie", "Gestion / management", "Creation / design",
           "Commerce / relation client", "Recherche / enseignement", "Entrepreneur / independant"]

EMOJI_FILIERE = {"IGGLIA": "💻", "ESIIA": "🔌", "IMTICIA": "🎬", "ISAIA": "📈",
                 "CAA": "💼", "FIC": "💰", "DTJA": "⚖️", "EMP": "📊",
                 "IAA": "🏭", "PIP": "💊", "AEE": "🌱",
                 "EMII": "⚙️", "GCA": "🏗️", "ICMP": "⛏️", "TEE": "🌍", "TEH": "🏨"}

SUGGESTIONS = [
    "⚖️ Compare ISAIA et IGGLIA en citant tes sources",
    "🎓 Quels diplômes délivre l'ISPM ?",
    "📋 Quelles séries de bac pour la biotechnologie ?",
    "🏫 Présente-moi la filière GCA",
]

PAGES = [("profil", "👤", "Mon Profil"), ("echanges", "💬", "Mes Échanges"),
         ("parcours", "🧭", "Parcours"), ("ressources", "📚", "Ressources"),
         ("parametres", "⚙️", "Paramètres")]

st.set_page_config(page_title="ORIENT'IA — Plateforme d'Orientation", page_icon="🎓",
                   layout="wide", initial_sidebar_state="expanded")

# ------------------------------------------------------------------- etat
st.session_state.setdefault("messages", [])
st.session_state.setdefault("page", "profil")
st.session_state.setdefault("theme_sombre", False)
st.session_state.setdefault("animations", True)
# Les cles des widgets profil doivent survivre au changement de page.
for _k, _d in [("k_serie", ""), ("k_matieres", []), ("k_interets", [])]:
    st.session_state.setdefault(_k, _d)
    st.session_state[_k] = st.session_state[_k]

SOMBRE = st.session_state.theme_sombre

# ------------------------------------------------------------------ styles
if SOMBRE:
    TH = {"fond": "#111814", "carte": "#1a241e", "ligne": "#2b382f", "encre": "#e5eae3",
          "gris": "#9aa596", "menthe_bloc": "#16american"}
    TH = {"fond": "#111814", "carte": "#1a241e", "ligne": "#2b382f", "encre": "#e5eae3",
          "gris": "#9aa596", "banniere": "#173425", "banniere_txt": "#a9d4b8"}
else:
    TH = {"fond": "#eef2ee", "carte": "#ffffff", "ligne": "#dfe7e1", "encre": "#1f2620",
          "gris": "#5b6459", "banniere": "#dff0e5", "banniere_txt": "#24523a"}

st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@500;600;700;800&family=Public+Sans:wght@400;500;600&display=swap');

  :root {{
    --vert-nuit: #0b3d2b; --vert: #14603f; --vert-vif: #1e7a4f; --menthe: #bff0d4;
    --fond: {TH['fond']}; --carte: {TH['carte']}; --ligne: {TH['ligne']};
    --encre: {TH['encre']}; --gris: {TH['gris']};
  }}
  html, body, [class*="css"] {{ font-family: 'Public Sans', 'Segoe UI', sans-serif; }}
  h1, h2, h3 {{ font-family: 'Outfit', sans-serif; color: var(--encre); }}
  .stApp {{ background: var(--fond); }}
  .stApp p, .stApp li, .stApp label p {{ color: var(--encre); }}
  .block-container {{ padding-top: 0.4rem; max-width: 64rem; }}
  #MainMenu, footer, header[data-testid="stHeader"] {{ visibility: hidden; height: 0; }}
  {"* { transition: none !important; animation: none !important; }" if not st.session_state.animations else ""}

  .topnav {{
    background: var(--vert-nuit); border-radius: 0 0 14px 14px;
    display: flex; align-items: center; justify-content: space-between;
    padding: 12px 22px; margin: 0 0 14px;
  }}
  .topnav .brand {{ color: #fff; font-family: 'Outfit'; font-weight: 800; font-size: 1.05rem; }}
  .topnav .links a {{ color: #cfe8d9; text-decoration: none; font-size: .78rem; font-weight: 600; margin-left: 18px; }}
  .topnav .links a:hover {{ color: #fff; }}

  .hero {{
    position: relative; overflow: hidden;
    background: linear-gradient(100deg, var(--vert-nuit) 0%, var(--vert) 80%);
    border-radius: 18px; padding: 24px 30px; color: #fff; margin-bottom: 14px;
    box-shadow: 0 10px 28px rgba(11, 61, 43, .25);
  }}
  .hero::after {{
    content: ""; position: absolute; right: 26px; top: 50%; transform: translateY(-50%);
    width: 140px; height: 140px; border-radius: 50%;
    background: linear-gradient(135deg, rgba(255,255,255,.16), rgba(255,255,255,.05));
  }}
  .hero h1 {{ color: #fff; font-size: 2rem; font-weight: 800; margin: 0; display: inline; vertical-align: middle; }}
  .hero .cap {{ font-size: 1.6rem; vertical-align: middle; margin-right: 8px; }}
  .hero .tagline {{ color: #cfe8d9; margin: 6px 0 12px; font-size: .93rem; }}
  .hero .chips span {{
    background: rgba(255,255,255,.13); border: 1px solid rgba(255,255,255,.28);
    color: #eaf6ef; font-size: .7rem; font-weight: 600; padding: 5px 13px;
    border-radius: 999px; margin-right: 8px;
  }}

  .stepper {{
    background: var(--carte); border: 1px solid var(--ligne); border-radius: 16px;
    display: flex; align-items: center; padding: 14px 24px; margin-bottom: 12px;
  }}
  .step {{ display: flex; flex-direction: column; align-items: center; gap: 5px; min-width: 128px; }}
  .step .dot {{
    width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center;
    justify-content: center; font-weight: 700; font-size: .85rem;
    background: var(--fond); color: var(--gris); border: 2px solid var(--ligne);
  }}
  .step.on .dot {{ background: var(--vert-vif); color: #fff; border-color: var(--vert-vif); }}
  .step .lbl {{ font-size: .74rem; font-weight: 700; color: var(--encre); text-align: center; }}
  .step .sub {{ font-size: .63rem; color: var(--gris); text-align: center; margin-top: -3px; }}
  .lien {{ flex: 1; height: 2px; background: var(--ligne); margin: 0 10px 24px; }}
  .lien.on {{ background: var(--vert-vif); }}

  .mention {{
    background: {TH['banniere']}; border: 1px solid var(--ligne); border-radius: 12px;
    padding: 10px 16px; font-size: .8rem; color: {TH['banniere_txt']}; margin-bottom: 16px;
  }}

  .page-titre h2 {{ font-size: 1.9rem; font-weight: 800; margin: 4px 0 2px; }}
  .page-titre p {{ color: var(--gris); font-size: .88rem; margin: 0 0 14px; }}

  .carte {{
    background: var(--carte); border: 1px solid var(--ligne); border-radius: 14px;
    padding: 16px 18px; margin-bottom: 12px; box-shadow: 0 3px 12px rgba(31, 60, 43, .06);
  }}
  .carte h4 {{ margin: 0 0 4px; font-family: 'Outfit'; color: var(--encre); font-size: 1rem; }}
  .carte .meta {{ font-size: .68rem; color: var(--gris); }}
  .carte .extrait {{ font-size: .8rem; color: var(--encre); margin: 6px 0; }}
  .tag {{
    display: inline-block; background: var(--fond); border: 1px solid var(--ligne);
    color: var(--gris); font-size: .62rem; font-weight: 700; letter-spacing: .04em;
    padding: 2px 9px; border-radius: 6px; margin-right: 6px;
  }}
  .tag.vert {{ background: var(--menthe); color: #0b3d2b; border-color: var(--menthe); }}

  .bloc-vert {{
    background: linear-gradient(135deg, var(--vert) 0%, var(--vert-vif) 100%);
    border-radius: 16px; padding: 18px 20px; color: #fff; margin-bottom: 12px;
  }}
  .bloc-vert h4 {{ color: #fff; margin: 0 0 6px; font-family: 'Outfit'; }}
  .bloc-vert p {{ color: #dff0e5 !important; font-size: .8rem; margin: 0; }}

  .route-item {{ display: flex; gap: 14px; margin-bottom: 4px; }}
  .route-item .pastille {{
    width: 30px; height: 30px; border-radius: 50%; flex: none; display: flex;
    align-items: center; justify-content: center; font-weight: 700; font-size: .8rem;
    background: var(--carte); border: 2px solid var(--ligne); color: var(--gris);
  }}
  .route-item.fait .pastille {{ background: var(--vert-vif); border-color: var(--vert-vif); color: #fff; }}
  .route-item .fil {{ width: 2px; flex: 1; background: var(--ligne); margin: 2px auto; min-height: 18px; }}
  .route-col {{ display: flex; flex-direction: column; align-items: center; }}
  .route-carte {{ flex: 1; background: var(--carte); border: 1px solid var(--ligne);
    border-radius: 12px; padding: 12px 16px; margin-bottom: 12px; }}
  .route-carte b {{ color: var(--encre); }}
  .route-carte .det {{ font-size: .76rem; color: var(--gris); margin-top: 3px; }}

  .carte-filiere {{
    background: var(--carte); border: 1.5px solid var(--ligne); border-radius: 14px;
    padding: 13px 15px 11px; height: 100%;
  }}
  .carte-filiere.premiere {{ border-color: var(--vert-vif); }}
  .carte-filiere .rang {{ display: inline-block; font-size: .62rem; font-weight: 700; color: var(--gris); margin-bottom: 4px; }}
  .carte-filiere.premiere .rang {{ background: var(--vert-vif); color: #fff; border-radius: 999px; padding: 2px 10px; }}
  .carte-filiere .sigle {{ font-family: 'Outfit'; font-size: 1.2rem; font-weight: 800; color: var(--encre); }}
  .carte-filiere .nom {{ font-size: .72rem; color: var(--gris); line-height: 1.35; min-height: 2.6em; }}
  .carte-filiere .barre {{ height: 7px; background: var(--ligne); border-radius: 99px; overflow: hidden; margin-top: 8px; }}
  .carte-filiere .barre div {{ height: 100%; background: linear-gradient(90deg, var(--vert), var(--vert-vif)); }}
  .carte-filiere .pct {{ font-family: 'Outfit'; font-weight: 800; color: var(--vert-vif); text-align: right; }}

  [data-testid="stChatMessage"] {{
    border-radius: 16px; padding: 15px 18px; margin-bottom: 12px;
    border: 1px solid var(--ligne); background: var(--carte);
  }}
  [data-testid="stChatInput"] {{
    border-radius: 999px; border: 1.5px solid var(--ligne); background: var(--carte);
  }}
  [data-testid="stChatInput"]:focus-within {{ border-color: var(--vert-vif); }}

  [data-testid="stSidebar"] {{ background: linear-gradient(180deg, var(--vert-nuit) 0%, #114a33 100%); }}
  [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{ color: #fff; }}
  [data-testid="stSidebar"] label p, [data-testid="stSidebar"] .stMarkdown p,
  [data-testid="stSidebar"] [data-testid="stCaptionContainer"],
  [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
  [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {{ color: #d9e8de !important; }}
  [data-testid="stSidebar"] [data-testid="stExpander"] {{
    background: rgba(255,255,255,.07); border-radius: 12px; border: 1px solid rgba(255,255,255,.18);
  }}
  [data-testid="stSidebar"] [data-testid="stExpander"] summary p,
  [data-testid="stSidebar"] [data-testid="stExpander"] summary span {{ color: #e8f2ec !important; }}
  [data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,.2); }}
  span[data-baseweb="tag"] {{ background: var(--vert) !important; border-radius: 999px; }}

  .logo-bloc {{ text-align: center; padding: 6px 0 4px; }}
  .logo-bloc .rond {{
    width: 56px; height: 56px; border-radius: 50%; background: #fff; margin: 0 auto 8px;
    display: flex; align-items: center; justify-content: center; font-size: 1.6rem;
  }}
  .logo-bloc .titre {{ color: #fff; font-family: 'Outfit'; font-weight: 800; font-size: 1.05rem; }}
  .logo-bloc .sous {{ color: #9fc4ae; font-size: .67rem; }}

  [data-testid="stSidebar"] .stButton button {{
    background: transparent; color: #cfe8d9; border: none; border-radius: 10px;
    font-size: .8rem; font-weight: 600; text-align: left; justify-content: flex-start;
  }}
  [data-testid="stSidebar"] .stButton button:hover:enabled {{
    background: rgba(255,255,255,.12); color: #fff; transform: none; box-shadow: none;
  }}
  [data-testid="stSidebar"] .stButton button[kind="primary"],
  [data-testid="stSidebar"] .stButton button[data-testid="stBaseButton-primary"] {{
    background: #ffffff; color: #0b3d2b; text-align: center; justify-content: center;
    border-radius: 999px; font-weight: 700;
  }}
  [data-testid="stSidebar"] .stButton button[kind="secondary"] {{
    background: var(--menthe); color: #0b3d2b; text-align: center; justify-content: center;
    border-radius: 999px; font-weight: 700;
  }}
  .stButton button {{
    border: 1.5px solid var(--vert); color: var(--encre); background: var(--carte);
    border-radius: 999px; font-size: .8rem; font-weight: 700;
  }}
  .stButton button:hover:enabled {{ background: var(--vert); color: #fff; }}
  .stButton button:disabled {{ opacity: .45; }}

  .footer-note {{
    text-align: center; color: var(--gris); font-size: .7rem;
    margin-top: 22px; padding-top: 12px; border-top: 1px solid var(--ligne);
  }}

  /* ------------------------------ responsive (telephone) ------------------ */
  @media (max-width: 740px) {{
    .block-container {{ padding-left: .6rem; padding-right: .6rem; }}
    .topnav {{ padding: 10px 14px; border-radius: 0 0 10px 10px; }}
    .topnav .links a {{ margin-left: 10px; font-size: .68rem; }}
    .hero {{ padding: 16px 16px; border-radius: 14px; }}
    .hero h1 {{ font-size: 1.35rem; }}
    .hero .cap {{ font-size: 1.2rem; }}
    .hero .tagline {{ font-size: .78rem; margin: 4px 0 10px; }}
    .hero::after {{ display: none; }}
    .hero .chips span {{ font-size: .58rem; padding: 3px 9px; margin: 0 5px 5px 0; display: inline-block; }}
    .stepper {{ padding: 10px 10px; }}
    .step {{ min-width: 84px; }}
    .step .dot {{ width: 24px; height: 24px; font-size: .72rem; }}
    .step .lbl {{ font-size: .6rem; }}
    .step .sub {{ display: none; }}
    .lien {{ margin: 0 4px 14px; }}
    .mention {{ font-size: .68rem; padding: 8px 12px; }}
    .page-titre h2 {{ font-size: 1.35rem; }}
    .page-titre p {{ font-size: .76rem; }}
    .carte {{ padding: 12px 13px; }}
    .carte-filiere .sigle {{ font-size: 1rem; }}
    .carte-filiere .nom {{ font-size: .62rem; min-height: 0; }}
    .carte-filiere .rang {{ font-size: .52rem; }}
    [data-testid="stChatMessage"] {{ padding: 11px 12px; border-radius: 12px; }}
    .route-carte {{ padding: 9px 11px; }}
    .route-carte .det {{ font-size: .68rem; }}
  }}
  /* empilement des colonnes (cartes top-3, suggestions, pages 2 colonnes) */
  @media (max-width: 640px) {{
    div[data-testid="stHorizontalBlock"] {{ flex-direction: column; gap: .5rem; }}
    div[data-testid="stHorizontalBlock"] > div {{ width: 100% !important; min-width: 100% !important; }}
  }}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------- helpers
@st.cache_data
def _registre_sources() -> dict:
    with open(ROOT / "data" / "registre_sources.csv", encoding="utf-8") as fh:
        return {r["id"]: r for r in csv.DictReader(fh)}


def _lire_traces(limite=60) -> list:
    lignes = []
    for fichier in sorted((ROOT / "traces").glob("interactions-*.jsonl"), reverse=True):
        for ligne in fichier.read_text(encoding="utf-8").splitlines():
            try:
                lignes.append(json.loads(ligne))
            except json.JSONDecodeError:
                continue
    lignes.sort(key=lambda t: t.get("ts", ""), reverse=True)
    return lignes[:limite]


def afficher_sources(texte: str):
    cites = sorted(set(re.findall(r"src-[a-z0-9-]+", texte)))
    if not cites:
        return
    registre = _registre_sources()
    with st.expander(f"📚 Sources citées ({len(cites)}) — registre officiel"):
        for sid in cites:
            r = registre.get(sid)
            if r:
                st.markdown(f"**[{sid}] {r['titre']}** · statut : {r['statut']} · "
                            f"consulté le {r['date_consultation']}\n\n"
                            f"<small>{r['origine_url']} — limites : {r['limites']}</small>",
                            unsafe_allow_html=True)
            else:
                st.markdown(f"**[{sid}]** — voir data/registre_sources.csv")


def questions_suivantes(meta) -> list:
    outils = [a["outil"] for a in meta["outils"]] if meta else []
    if meta and meta.get("refus"):
        return ["Quels parcours me correspondent ?",
                "Cette recommandation repose-t-elle sur des données réelles ou générées ?"]
    for a in (meta["outils"] if meta else []):
        if a["outil"] == "analyser_profil_ml" and "top3" in a.get("sortie", {}):
            s = [t["sigle"] for t in a["sortie"]["top3"]]
            return ["Pourquoi ton modèle recommande-t-il ce parcours ?",
                    f"Compare {s[0]} et {s[1]}",
                    f"Quels sont les prérequis de bac pour {s[0]} ?"]
        if a["outil"] == "comparer_parcours":
            comp = a["sortie"].get("comparaison", [])
            if len(comp) == 2:
                return [f"Quels sont les prérequis de bac pour {comp[0]['sigle']} ?",
                        f"Quels sont les débouchés de la filière {comp[1]['sigle']} ?",
                        "Quels parcours me correspondent ?"]
        if a["outil"] == "verifier_prerequis":
            sigle = a["sortie"].get("filiere", "")
            return [f"Présente-moi la filière {sigle}",
                    f"Quels sont les débouchés de la filière {sigle} ?",
                    "Quels parcours me correspondent ?"]
    if "rechercher_formation" in outils:
        return ["Quels parcours me correspondent ?",
                "Quelles sont les conditions d'accès en première année ?",
                "Compare ISAIA et IGGLIA"]
    return []


def traiter(question: str):
    st.session_state.messages.append({"role": "user", "contenu": question, "meta": None})
    r = agent.repondre(question, profil)
    meta = {k: r[k] for k in ["outils", "latence_ms", "refus", "mode"]}
    st.session_state.messages.append({"role": "assistant", "contenu": r["reponse"], "meta": meta})
    for a in meta["outils"]:
        if a["outil"] == "analyser_profil_ml" and "top3" in a.get("sortie", {}):
            st.session_state.derniere_reco = a["sortie"]


def cartes_top3(meta):
    for a in meta["outils"]:
        if a["outil"] == "analyser_profil_ml" and "top3" in a.get("sortie", {}):
            top3 = a["sortie"]["top3"]
            colonnes = st.columns(len(top3))
            for i, (col, t) in enumerate(zip(colonnes, top3)):
                pct = round(t["probabilite"] * 100)
                col.markdown(f"""
<div class="carte-filiere {'premiere' if i == 0 else ''}">
  <span class="rang">{'◉ MEILLEURE CORRESPONDANCE' if i == 0 else f'#{i + 1}'}</span>
  <div class="sigle">{EMOJI_FILIERE.get(t['sigle'], '🎓')} {t['sigle']}</div>
  <div class="nom">{t['nom']}</div>
  <div class="barre"><div style="width:{max(pct, 3)}%"></div></div>
  <div class="pct">{pct} %</div>
</div>""", unsafe_allow_html=True)
            return


def topnav():
    st.markdown("""
    <div class="topnav"><span class="brand">Guidance IA</span>
      <span class="links"><a href="https://ispm-edu.com" target="_blank">Site ISPM</a>
      <a href="mailto:contact@ispm.education">Contact</a></span></div>
    """, unsafe_allow_html=True)


# ----------------------------------------------------------- barre laterale
with st.sidebar:
    st.markdown("""
    <div class="logo-bloc"><div class="rond">🎓</div>
      <div class="titre">ORIENT'IA</div><div class="sous">Plateforme d'Orientation</div></div>
    """, unsafe_allow_html=True)

    for pid, ico, nom in PAGES:
        actif = "▶ " if st.session_state.page == pid else ""
        if st.button(f"{ico}  {actif}{nom}", key=f"nav-{pid}", use_container_width=True):
            st.session_state.page = pid
            st.rerun()

    st.divider()

    if st.session_state.page == "profil":
        serie = st.selectbox("🎯 Série de bac *", [""] + tools.SERIES, key="k_serie")
        matieres = st.multiselect("📚 Matières préférées * (max 3)", MATIERES,
                                  max_selections=3, key="k_matieres")
        interets = st.multiselect("💡 Centres d'intérêt * (max 4)", INTERETS,
                                  max_selections=4, key="k_interets")
        with st.expander("📊 Mes niveaux (1 → 5)"):
            note_maths = st.slider("Mathématiques", 1, 5, 3)
            note_sciences = st.slider("Sciences", 1, 5, 3)
            note_langues = st.slider("Langues", 1, 5, 3)
            note_eco = st.slider("Éco-gestion", 1, 5, 3)
        with st.expander("➕ Affiner (facultatif)"):
            competences = st.multiselect("Compétences", COMPETENCES)
            environnement = st.selectbox("Environnement de travail", ENVIRONNEMENTS)
            metiers = st.multiselect("Métier visé (max 2)", METIERS, max_selections=2)

        profil = {"serie_bac": serie, "note_maths": note_maths, "note_sciences": note_sciences,
                  "note_langues": note_langues, "note_eco": note_eco,
                  "matieres_preferees": matieres, "competences": competences,
                  "interets": interets, "environnement": environnement, "metiers_vises": metiers}
        st.session_state.profil_sauve = profil

        remplis = sum(bool(v) for v in [serie, matieres, interets, competences, environnement, metiers])
        st.progress(remplis / 6, text=f"Profil : {remplis}/6")
        pret = bool(serie and matieres and interets)
        if not pret:
            manques = [n for n, v in [("série de bac", serie), ("matières", matieres),
                                      ("intérêts", interets)] if not v]
            st.caption("✏️ Il manque : " + ", ".join(manques))

        st.divider()
        if st.button("🧭 Obtenir ma recommandation", type="primary",
                     use_container_width=True, disabled=not pret):
            traiter("Quels parcours me correspondent ?")
            st.rerun()
        if st.button("＋ Nouvelle Session", type="secondary", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    else:
        profil = st.session_state.get("profil_sauve") or {
            "serie_bac": st.session_state.k_serie, "note_maths": 3, "note_sciences": 3,
            "note_langues": 3, "note_eco": 3, "matieres_preferees": st.session_state.k_matieres,
            "competences": [], "interets": st.session_state.k_interets,
            "environnement": "", "metiers_vises": []}
        pret = bool(profil.get("serie_bac") and profil.get("matieres_preferees")
                    and profil.get("interets"))

    if agent.os.environ.get("ANTHROPIC_API_KEY"):
        st.caption("Mode : 🔑 LLM Anthropic")
    elif agent.os.environ.get("GEMINI_API_KEY"):
        st.caption("Mode : 🔑 LLM Gemini (gratuit)")
    elif agent.os.environ.get("GROQ_API_KEY"):
        st.caption("Mode : 🔑 LLM Groq (gratuit)")
    else:
        st.caption("Mode : ⚙️ Déterministe · 100 % local")

# Mini-formulaire du chat valide -> recommandation immediate.
if st.session_state.pop("auto_reco", False):
    traiter("Quels parcours me correspondent ?")

page = st.session_state.page

# =====================================================  PAGE : MON PROFIL
if page == "profil":
    a_pose_question = any(m["role"] == "user" for m in st.session_state.messages)
    a_recommandation = any(m.get("meta") and any(o["outil"] == "analyser_profil_ml"
                                                 for o in m["meta"]["outils"])
                           for m in st.session_state.messages if m.get("meta"))
    topnav()
    st.markdown(f"""
    <div class="hero"><span class="cap">🎓</span><h1>ORIENT'IA</h1>
      <p class="tagline">Assistant intelligent d'orientation — 16 filières</p>
      <div class="chips"><span>◉ Sources officielles citées</span><span>☑ 38/38 tests</span>
      <span>◈ Modèle ML expliqué</span></div></div>
    <div class="stepper">
      <div class="step {'on' if pret else ''}"><div class="dot">{'✓' if pret else '1'}</div>
        <div class="lbl">Remplir mon profil</div><div class="sub">panneau de gauche</div></div>
      <div class="lien {'on' if pret else ''}"></div>
      <div class="step {'on' if a_pose_question else ''}"><div class="dot">{'✓' if a_pose_question else '2'}</div>
        <div class="lbl">Poser une question</div><div class="sub">ou « Obtenir ma recommandation »</div></div>
      <div class="lien {'on' if a_recommandation else ''}"></div>
      <div class="step {'on' if a_recommandation else ''}"><div class="dot">{'✓' if a_recommandation else '3'}</div>
        <div class="lbl">Explorer les résultats</div><div class="sub">top 3 · sources · traces</div></div>
    </div>
    <div class="mention">ℹ️ ORIENT'IA constitue un outil d'aide à l'orientation. Ses recommandations ne
    remplacent ni l'avis d'un conseiller pédagogique ni une décision officielle d'admission.</div>
    """, unsafe_allow_html=True)

    if not st.session_state.messages:
        with st.chat_message("assistant", avatar="🎓"):
            st.markdown("Bonjour 👋 Je suis **ORIENT'IA**. Remplissez votre profil à gauche puis "
                        "cliquez sur **🧭 Obtenir ma recommandation** — ou posez-moi directement "
                        "une question sur les filières de l'ISPM :")

    for m in st.session_state.messages:
        avatar = "🎓" if m["role"] == "assistant" else "🧑"
        with st.chat_message(m["role"], avatar=avatar):
            if m.get("meta"):
                cartes_top3(m["meta"])
            st.markdown(m["contenu"])
            if m.get("meta"):
                afficher_sources(m["contenu"])
                meta = m["meta"]
                etiquette = f"🔍 Traces — {meta['latence_ms']} ms · mode {meta['mode']}"
                if meta["refus"]:
                    etiquette += f" · 🛡️ REFUS ({meta['refus']})"
                with st.expander(etiquette):
                    for a in meta["outils"]:
                        st.markdown(f"**Outil `{a['outil']}`**")
                        st.json({"entrée": a["entree"], "sortie": a["sortie"]}, expanded=False)
                    if not meta["outils"]:
                        st.caption("Aucun outil appelé (refus de sécurité ou réponse directe).")
                    st.caption("Trace complète : dossier traces/ (JSONL).")

    def _appliquer_profil_chat():
        st.session_state.k_serie = st.session_state.kf_serie
        st.session_state.k_matieres = st.session_state.kf_matieres
        st.session_state.k_interets = st.session_state.kf_interets
        st.session_state.auto_reco = True

    _dm = st.session_state.messages[-1] if st.session_state.messages else None
    if _dm and _dm["role"] == "assistant" and "il me manque" in _dm["contenu"]:
        with st.chat_message("assistant", avatar="📋"):
            st.markdown("**Complétez votre profil directement ici :**")
            with st.form("profil_chat"):
                st.selectbox("🎯 Série de bac", [""] + tools.SERIES, key="kf_serie")
                st.multiselect("📚 Matières préférées (max 3)", MATIERES,
                               max_selections=3, key="kf_matieres")
                st.multiselect("💡 Centres d'intérêt (max 4)", INTERETS,
                               max_selections=4, key="kf_interets")
                st.form_submit_button("✅ Valider et obtenir ma recommandation",
                                      type="primary", on_click=_appliquer_profil_chat)

    dernier = st.session_state.messages[-1] if st.session_state.messages else None
    suivantes = questions_suivantes(dernier["meta"]) if dernier and dernier.get("meta") else []
    if suivantes:
        st.caption("💡 Pour continuer :")
        colonnes = st.columns(len(suivantes))
        for i, (col, q) in enumerate(zip(colonnes, suivantes)):
            if col.button(q, key=f"suiv-{len(st.session_state.messages)}-{i}",
                          use_container_width=True):
                with st.spinner("Analyse en cours…"):
                    traiter(q)
                st.rerun()
    else:
        colonnes = st.columns(len(SUGGESTIONS))
        for col, s in zip(colonnes, SUGGESTIONS):
            if col.button(s, key=f"sugg-{s[:14]}", use_container_width=True):
                with st.spinner("Analyse en cours…"):
                    traiter(s.split(" ", 1)[1])
                st.rerun()

    if question := st.chat_input("Posez votre question sur les filières, prérequis, débouchés…"):
        with st.spinner("Analyse en cours…"):
            traiter(question)
        st.rerun()

# ===================================================  PAGE : MES ECHANGES
elif page == "echanges":
    topnav()
    st.markdown('<div class="page-titre"><h2>Mes Échanges</h2>'
                '<p>Historique réel de vos conversations avec l\'assistant '
                '(lu depuis les traces JSONL — observabilité du sujet).</p></div>',
                unsafe_allow_html=True)
    col_g, col_d = st.columns([2.2, 1])
    with col_g:
        recherche = st.text_input("🔍 Rechercher une conversation…", key="cherche_traces",
                                  label_visibility="collapsed",
                                  placeholder="🔍 Rechercher une conversation…")
        traces = _lire_traces()
        if recherche:
            traces = [t for t in traces if recherche.lower() in t.get("question", "").lower()]
        if not traces:
            st.info("Aucune interaction trouvée.")
        for t in traces[:15]:
            date = t.get("ts", "")[:16].replace("T", " · ")
            refus = t.get("refus")
            outils = {a["outil"] for a in t.get("outils", [])}
            tags = "".join(f'<span class="tag">{o.replace("_", " ").upper()}</span>' for o in list(outils)[:2])
            if refus:
                tags += '<span class="tag vert">REFUS SÉCURITÉ</span>'
            extrait = (t.get("reponse", "").replace("*", "").replace("#", "")[:180] + "…")
            st.markdown(f"""
            <div class="carte"><h4>{t.get('question', '(sans question)')[:80]}</h4>
              <span class="meta">{date} · {t.get('latence_ms', '?')} ms · mode {t.get('mode', '?')}</span>
              <div class="extrait">{extrait}</div>{tags}</div>
            """, unsafe_allow_html=True)
    with col_d:
        st.markdown("""
        <div class="bloc-vert"><h4>💬 Nouvel Échange</h4>
          <p>Démarrez une nouvelle session d'orientation avec l'IA.</p></div>
        """, unsafe_allow_html=True)
        if st.button("Démarrer", type="primary", use_container_width=True):
            st.session_state.messages = []
            st.session_state.page = "profil"
            st.rerun()
        toutes = _lire_traces(1000)
        n_refus = sum(1 for t in toutes if t.get("refus"))
        remplis = sum(bool(v) for v in [profil.get("serie_bac"), profil.get("matieres_preferees"),
                                        profil.get("interets"), profil.get("competences"),
                                        profil.get("environnement"), profil.get("metiers_vises")])
        st.markdown(f"""
        <div class="carte"><h4>Vos statistiques</h4>
          <p style="font-size:.8rem">💬 Interactions tracées : <b>{len(toutes)}</b><br>
          🛡️ Refus de sécurité : <b>{n_refus}</b><br>
          👤 Complétion du profil : <b>{round(100 * remplis / 6)} %</b></p></div>
        """, unsafe_allow_html=True)

# =====================================================  PAGE : PARCOURS
elif page == "parcours":
    topnav()
    reco = st.session_state.get("derniere_reco")
    sigle_defaut = reco["top3"][0]["sigle"] if reco else "IGGLIA"
    st.markdown('<div class="page-titre"><h2>Parcours Recommandé</h2>'
                '<p>Feuille de route officielle du système LMD de l\'ISPM '
                '(source : brochure août 2025) pour la filière choisie.</p></div>',
                unsafe_allow_html=True)
    sigles_tous = sorted(tools._PAR_SIGLE)
    sigle = st.selectbox("Filière", sigles_tous, index=sigles_tous.index(sigle_defaut),
                         format_func=lambda s: f"{EMOJI_FILIERE.get(s, '')} {s} — {tools._PAR_SIGLE[s]['nom']}")
    f = tools._PAR_SIGLE[sigle]
    col_g, col_d = st.columns([2.1, 1])
    with col_g:
        etapes = [
            ("Sélection de dossier", "Dossier de candidature complet ; entretien programmé si besoin. "
             "Prérequis : " + f["prerequis_bac"], True),
            ("Premier cycle — Licence (L1 → L3)", "3 années menant au diplôme de Licence (BAC+3), "
             "habilitation LMD 2015.", False),
            ("Second cycle — Master / Ingénorat (M1, M2)", "2 années menant au Master (BAC+5), "
             "également appelé Ingénorat.", False),
            ("Troisième cycle — Doctorat", "Années de recherche pour la préparation du doctorat.", False),
        ]
        st.markdown('<div class="carte"><h4>Feuille de Route</h4></div>', unsafe_allow_html=True)
        for i, (titre, det, fait) in enumerate(etapes, 1):
            fil = '<div class="fil"></div>' if i < len(etapes) else ''
            st.markdown(f"""
            <div class="route-item {'fait' if fait else ''}">
              <div class="route-col"><div class="pastille">{'✓' if fait else i}</div>{fil}</div>
              <div class="route-carte"><b>{titre}</b><div class="det">{det}</div></div>
            </div>""", unsafe_allow_html=True)
        st.caption("_Source : schéma « Cursus à l'ISPM » [src-brochure-papier] · conditions "
                   "d'accès [src-inscription]._")
    with col_d:
        st.markdown(f"""
        <div class="carte"><h4>Vue d'ensemble — {sigle}</h4>
          <p style="font-size:.78rem">🏛️ Mention : <b>{next((m for m, s in tools._FORMATIONS['mentions_lmd']['mentions'].items() if sigle in s), f['departement'])}</b><br>
          🎯 Prérequis : <b>{f['prerequis_bac']}</b><br>
          💼 Débouchés : <b>{', '.join(f['debouches'] or ['non précisés par les sources'])}</b></p></div>
        """, unsafe_allow_html=True)
        if reco:
            facteurs = ", ".join(reco.get("facteurs_principaux", [])[:3]) or "n/d"
            st.markdown(f"""
            <div class="bloc-vert"><h4>💡 Conseil de l'IA</h4>
              <p>D'après votre profil déclaré, {reco['top3'][0]['sigle']} arrive en tête
              ({reco['top3'][0]['probabilite']:.0%}). Facteurs du modèle : {facteurs}.
              Score = aide à la décision, pas un verdict.</p></div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="bloc-vert"><h4>💡 Conseil de l'IA</h4>
              <p>Remplissez votre profil puis demandez une recommandation : cette carte
              affichera les facteurs réels du modèle pour votre top 1.</p></div>
            """, unsafe_allow_html=True)

# ===================================================  PAGE : RESSOURCES
elif page == "ressources":
    topnav()
    st.markdown('<div class="page-titre"><h2>Centre de Ressources</h2>'
                '<p>Les sources officielles du corpus (registre de traçabilité) et les '
                'documents produits par le projet.</p></div>', unsafe_allow_html=True)
    st.markdown("#### 📜 Sources officielles (registre)")
    regs = list(_registre_sources().values())
    for rang in range(0, len(regs), 2):
        cols = st.columns(2)
        for col, r in zip(cols, regs[rang:rang + 2]):
            col.markdown(f"""
            <div class="carte"><h4>{r['titre'][:70]}</h4>
              <span class="meta">[{r['id']}] · consulté le {r['date_consultation']}</span>
              <div class="extrait">{r['donnees_extraites'][:150]}…</div>
              <span class="tag vert">{r['statut'].upper()}</span></div>
            """, unsafe_allow_html=True)
    st.markdown("#### 📂 Documents du projet")
    docs = [("Rapport ML", "models/RAPPORT-ML.md", "Comparaison des modèles, métriques top-k, calibration"),
            ("Transfert synthétique → réel", "models/RAPPORT-TRANSFERT.md", "79 réponses réelles : top-3 0,73 ± 0,10"),
            ("Limites, biais et risques", "docs/limites_biais_risques.md", "Le tableau risque → défense → preuve"),
            ("Résultats d'évaluation", "eval/RESULTATS.md", "38 cas / 9 catégories — 38/38 réussis"),
            ("Apport de l'IA symbolique", "eval/APPORT-GRAPHE.md", "2,3 % des top-1 ML corrigés par les règles"),
            ("Architecture", "docs/architecture.png", "Schéma des deux chaînes de données")]
    for rang in range(0, len(docs), 3):
        cols = st.columns(3)
        for col, (titre, chemin, det) in zip(cols, docs[rang:rang + 3]):
            col.markdown(f"""
            <div class="carte"><h4>📄 {titre}</h4>
              <div class="extrait">{det}</div><span class="meta">{chemin}</span></div>
            """, unsafe_allow_html=True)

# ==================================================  PAGE : PARAMETRES
elif page == "parametres":
    topnav()
    st.markdown('<div class="page-titre"><h2>Paramètres</h2>'
                '<p>Préférences d\'affichage de la plateforme.</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="carte"><h4>🎨 Thème</h4></div>', unsafe_allow_html=True)
    sombre = st.toggle("🌙 Mode sombre", value=st.session_state.theme_sombre,
                       help="Bascule l'interface en thème sombre")
    anim = st.toggle("✨ Animations et transitions", value=st.session_state.animations,
                     help="Désactiver pour réduire les effets visuels")
    if sombre != st.session_state.theme_sombre or anim != st.session_state.animations:
        st.session_state.theme_sombre = sombre
        st.session_state.animations = anim
        st.rerun()
    st.caption("Aucun compte, aucune donnée personnelle : le profil déclaré reste local à la "
               "session (exigence d'anonymat du sujet).")

st.markdown('<div class="footer-note">Prototype académique — Examen de fin d\'études M2, ISPM · '
            'Données : site officiel + brochure août 2025 · Traces complètes dans traces/ (JSONL)</div>',
            unsafe_allow_html=True)
