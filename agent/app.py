"""Interface ORIENT'IA (Streamlit).

Lancement :  streamlit run agent/app.py
Le profil est DECLARE par l'utilisateur dans la barre laterale (collecte
progressive) ; l'assistant n'infere rien. Chaque reponse expose ses traces
(outils appeles, scores, latence) et la mention obligatoire est affichee en
permanence (exigences du sujet).
"""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))
import agent  # noqa: E402
import tools  # noqa: E402

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

SUGGESTIONS = [
    "🧭 Quels parcours me correspondent ?",
    "⚖️ Compare ISAIA et IGGLIA en citant tes sources",
    "🎓 Quels diplômes délivre l'ISPM ?",
    "📋 Quelles séries de bac pour la biotechnologie ?",
]

st.set_page_config(page_title="ORIENT'IA — ISPM", page_icon="🎓", layout="wide",
                   initial_sidebar_state="expanded")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@500;600;700&family=Public+Sans:wght@400;500;600&display=swap');

  html, body, [class*="css"] { font-family: 'Public Sans', 'Segoe UI', sans-serif; }
  h1, h2, h3 { font-family: 'Outfit', 'Segoe UI', sans-serif; }
  .block-container { padding-top: 1.3rem; max-width: 60rem; }
  #MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }

  .orientia-hero {
    position: relative; overflow: hidden;
    background: linear-gradient(115deg, #0d3b23 0%, #1e6b45 55%, #2e8a5c 100%);
    border-radius: 18px; padding: 30px 34px 24px; color: #ffffff; margin-bottom: 8px;
    box-shadow: 0 10px 30px rgba(13, 59, 35, .25);
  }
  .orientia-hero::before {
    content: ""; position: absolute; right: -60px; top: -60px; width: 240px; height: 240px;
    background: radial-gradient(circle, rgba(255,255,255,.14) 0%, transparent 65%);
  }
  .orientia-hero::after {
    content: ""; position: absolute; left: 30%; bottom: -90px; width: 260px; height: 260px;
    background: radial-gradient(circle, rgba(255,255,255,.08) 0%, transparent 60%);
  }
  .orientia-hero h1 {
    color: #ffffff; font-size: 2.35rem; font-weight: 700; letter-spacing: .01em; margin: 0 0 4px;
  }
  .orientia-hero .tagline { color: #cfe8d9; margin: 0 0 14px; font-size: .98rem; }
  .hero-chips { display: flex; flex-wrap: wrap; gap: 8px; }
  .hero-chips span {
    background: rgba(255,255,255,.14); border: 1px solid rgba(255,255,255,.25);
    color: #eaf6ef; font-size: .74rem; font-weight: 600; letter-spacing: .03em;
    padding: 4px 12px; border-radius: 999px;
  }

  .mention {
    background: #eef5f0; border: 1px solid #d5e5da; border-left: 5px solid #1e6b45;
    border-radius: 0 10px 10px 0; padding: 10px 16px; font-size: .82rem;
    color: #2c4636; margin: 12px 0 20px;
  }

  [data-testid="stChatMessage"] {
    border-radius: 14px; padding: 15px 18px; margin-bottom: 12px;
    border: 1px solid #e2eae4; background: #ffffff;
    box-shadow: 0 2px 10px rgba(31, 60, 43, .05);
  }
  [data-testid="stChatMessage"]:has([aria-label="Chat message from user"]) {
    background: #eaf3ed; border-color: #d3e4d9;
  }

  [data-testid="stSidebar"] { background: linear-gradient(180deg, #eef4f0 0%, #e6efe9 100%); }
  [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 {
    color: #145032; font-family: 'Outfit', sans-serif;
  }
  [data-testid="stSidebar"] [data-testid="stExpander"] {
    background: #ffffff; border-radius: 10px; border: 1px solid #dbe7de;
  }

  .stButton button {
    border: 1.5px solid #1e6b45; color: #145032; background: #ffffff;
    border-radius: 999px; font-size: .82rem; font-weight: 600; padding: 6px 16px;
    transition: all .15s ease;
  }
  .stButton button:hover {
    background: #1e6b45; color: #ffffff; border-color: #1e6b45;
    transform: translateY(-1px); box-shadow: 0 4px 12px rgba(30, 107, 69, .30);
  }

  div[data-testid="stExpander"] summary { font-size: .85rem; }
  .footer-note {
    text-align: center; color: #7d8a80; font-size: .74rem;
    margin-top: 26px; padding-top: 14px; border-top: 1px solid #e2eae4;
  }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="orientia-hero">
  <h1>🎓 ORIENT'IA</h1>
  <p class="tagline">Assistant intelligent d'orientation — Institut Supérieur Polytechnique de Madagascar</p>
  <div class="hero-chips">
    <span>16 FILIÈRES</span><span>SOURCES OFFICIELLES CITÉES</span><span>MODÈLE ML EXPLIQUÉ</span>
    <span>INCERTITUDE DÉCLARÉE</span><span>32/32 TESTS</span>
  </div>
</div>
<div class="mention">ℹ️ ORIENT'IA constitue un outil d'aide à l'orientation. Ses recommandations ne
remplacent ni l'avis d'un conseiller pédagogique ni une décision officielle d'admission.</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------------- profil declare
with st.sidebar:
    st.header("👤 Mon profil")
    st.caption("L'assistant n'utilise que ce que vous déclarez ici — jamais votre style d'écriture.")

    serie = st.selectbox("🎯 Série de bac", [""] + tools.SERIES)
    matieres = st.multiselect("📚 Matières préférées (max 3)", MATIERES, max_selections=3)
    interets = st.multiselect("💡 Centres d'intérêt (max 4)", INTERETS, max_selections=4)
    with st.expander("📊 Mes niveaux (1 → 5)"):
        note_maths = st.slider("Mathématiques", 1, 5, 3)
        note_sciences = st.slider("Sciences", 1, 5, 3)
        note_langues = st.slider("Langues", 1, 5, 3)
        note_eco = st.slider("Éco-gestion", 1, 5, 3)
    with st.expander("➕ Compléter mon profil"):
        competences = st.multiselect("Compétences", COMPETENCES)
        environnement = st.selectbox("Environnement de travail", ENVIRONNEMENTS)
        metiers = st.multiselect("Métier visé (max 2)", METIERS, max_selections=2)

    remplis = sum(bool(v) for v in [serie, matieres, interets, competences, environnement, metiers])
    st.progress(remplis / 6, text=f"Profil : {remplis}/6 sections remplies")
    if remplis < 3:
        st.caption("⚠️ Série, matières et intérêts sont nécessaires pour une recommandation.")

    st.divider()
    if st.button("🧹 Nouvelle conversation", use_container_width=True):
        st.session_state.pop("messages", None)
        st.rerun()
    if agent.os.environ.get("ANTHROPIC_API_KEY"):
        st.caption("Mode agent : 🔑 LLM Anthropic")
    elif agent.os.environ.get("GEMINI_API_KEY"):
        st.caption("Mode agent : 🔑 LLM Gemini (gratuit)")
    else:
        st.caption("Mode agent : ⚙️ Déterministe · 100 % local")

profil = {"serie_bac": serie, "note_maths": note_maths, "note_sciences": note_sciences,
          "note_langues": note_langues, "note_eco": note_eco,
          "matieres_preferees": matieres, "competences": competences, "interets": interets,
          "environnement": environnement, "metiers_vises": metiers}

# ------------------------------------------------------------------ chat
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "contenu":
        "Bonjour 👋 Je suis **ORIENT'IA**, l'assistant d'orientation de l'ISPM.\n\n"
        "Renseignez votre profil à gauche, puis posez vos questions — ou utilisez les "
        "suggestions ci-dessous : présentation d'une filière, comparaison, prérequis, "
        "recommandation personnalisée…", "meta": None}]


def traiter(question: str):
    st.session_state.messages.append({"role": "user", "contenu": question, "meta": None})
    r = agent.repondre(question, profil)
    st.session_state.messages.append({"role": "assistant", "contenu": r["reponse"],
                                      "meta": {k: r[k] for k in ["outils", "latence_ms", "refus", "mode"]}})


for m in st.session_state.messages:
    avatar = "🎓" if m["role"] == "assistant" else "🧑"
    with st.chat_message(m["role"], avatar=avatar):
        st.markdown(m["contenu"])
        if m.get("meta"):
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

# Suggestions cliquables (utile pour la demo et la video).
if len(st.session_state.messages) <= 1:
    colonnes = st.columns(2)
    for i, s in enumerate(SUGGESTIONS):
        if colonnes[i % 2].button(s, key=f"sugg-{i}", use_container_width=True):
            with st.spinner("Analyse en cours…"):
                traiter(s.split(" ", 1)[1])
            st.rerun()

if question := st.chat_input("Posez votre question…"):
    with st.spinner("Analyse en cours…"):
        traiter(question)
    st.rerun()

st.markdown('<div class="footer-note">Prototype académique — Examen de fin d\'études M2, ISPM · '
            'Données : site officiel + brochure août 2025 · Traces complètes dans traces/ (JSONL)</div>',
            unsafe_allow_html=True)
