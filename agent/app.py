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
    "Quels parcours me correspondent ?",
    "Compare ISAIA et IGGLIA en citant tes sources",
    "Quelles séries de bac pour la biotechnologie ?",
    "Quels diplômes délivre l'ISPM ?",
]

st.set_page_config(page_title="ORIENT'IA — ISPM", page_icon="🎓", layout="wide",
                   initial_sidebar_state="expanded")

st.markdown("""
<style>
  .block-container { padding-top: 1.6rem; max-width: 62rem; }
  #MainMenu, footer { visibility: hidden; }
  .orientia-header {
    background: linear-gradient(120deg, #1e6b45 0%, #2e8a5c 100%);
    border-radius: 14px; padding: 22px 28px 18px; color: #ffffff; margin-bottom: 6px;
  }
  .orientia-header h1 { color: #ffffff; font-size: 2rem; margin: 0 0 2px; }
  .orientia-header p { color: #d8ecdf; margin: 0; font-size: .95rem; }
  .mention {
    background: #e9f1ec; border-left: 4px solid #1e6b45; border-radius: 0 8px 8px 0;
    padding: 8px 14px; font-size: .82rem; color: #2c4636; margin: 10px 0 18px;
  }
  [data-testid="stChatMessage"] {
    background: #ffffff; border: 1px solid #dfe7e1; border-radius: 12px;
    padding: 14px 16px; margin-bottom: 10px;
  }
  [data-testid="stSidebar"] { background: #eef4f0; }
  [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 { color: #1e6b45; }
  div[data-testid="stExpander"] { border-radius: 10px; }
  .stButton button {
    border: 1px solid #1e6b45; color: #145032; background: #ffffff;
    border-radius: 999px; font-size: .82rem; padding: 4px 14px;
  }
  .stButton button:hover { background: #e9f1ec; color: #0d3b23; border-color: #145032; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="orientia-header">
  <h1>🎓 ORIENT'IA</h1>
  <p>Assistant intelligent d'orientation — Institut Supérieur Polytechnique de Madagascar ·
  16 filières · sources officielles citées · incertitude déclarée</p>
</div>
<div class="mention">ℹ️ ORIENT'IA constitue un outil d'aide à l'orientation. Ses recommandations ne
remplacent ni l'avis d'un conseiller pédagogique ni une décision officielle d'admission.</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------------- profil declare
with st.sidebar:
    st.header("👤 Mon profil")
    st.caption("L'assistant n'utilise que ce que vous déclarez ici — jamais votre style d'écriture.")

    serie = st.selectbox("🎯 Série de bac", [""] + tools.SERIES)
    with st.expander("📊 Mes niveaux (1 → 5)", expanded=False):
        note_maths = st.slider("Mathématiques", 1, 5, 3)
        note_sciences = st.slider("Sciences", 1, 5, 3)
        note_langues = st.slider("Langues", 1, 5, 3)
        note_eco = st.slider("Éco-gestion", 1, 5, 3)
    matieres = st.multiselect("📚 Matières préférées (max 3)", MATIERES, max_selections=3)
    interets = st.multiselect("💡 Centres d'intérêt (max 4)", INTERETS, max_selections=4)
    with st.expander("➕ Compléter mon profil", expanded=False):
        competences = st.multiselect("Compétences", COMPETENCES)
        environnement = st.selectbox("Environnement de travail", ENVIRONNEMENTS)
        metiers = st.multiselect("Métier visé (max 2)", METIERS, max_selections=2)

    remplis = sum(bool(v) for v in [serie, matieres, interets, competences, environnement, metiers])
    st.progress(remplis / 6, text=f"Profil : {remplis}/6 sections remplies")
    if remplis < 3:
        st.caption("⚠️ Série, matières et intérêts sont nécessaires pour une recommandation.")

    st.divider()
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
    st.caption("Suggestions :")
    colonnes = st.columns(len(SUGGESTIONS))
    for col, s in zip(colonnes, SUGGESTIONS):
        if col.button(s, key=f"sugg-{s[:20]}"):
            with st.spinner("Analyse en cours…"):
                traiter(s)
            st.rerun()

if question := st.chat_input("Posez votre question…"):
    with st.spinner("Analyse en cours…"):
        traiter(question)
    st.rerun()
