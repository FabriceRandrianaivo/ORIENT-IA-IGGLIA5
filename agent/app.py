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

st.set_page_config(page_title="ORIENT'IA — ISPM", page_icon="🎓", layout="wide")

st.title("🎓 ORIENT'IA")
st.info(agent.MENTION, icon="ℹ️")

# ----------------------------------------------------------- profil declare
with st.sidebar:
    st.header("Mon profil déclaré")
    st.caption("L'assistant n'utilise que ce que vous déclarez ici — jamais votre style d'écriture.")
    serie = st.selectbox("Série de bac", [""] + tools.SERIES)
    c1, c2 = st.columns(2)
    note_maths = c1.slider("Maths", 1, 5, 3)
    note_sciences = c2.slider("Sciences", 1, 5, 3)
    note_langues = c1.slider("Langues", 1, 5, 3)
    note_eco = c2.slider("Éco-gestion", 1, 5, 3)
    matieres = st.multiselect("Matières préférées (max 3)", MATIERES, max_selections=3)
    competences = st.multiselect("Compétences", COMPETENCES)
    interets = st.multiselect("Centres d'intérêt (max 4)", INTERETS, max_selections=4)
    environnement = st.selectbox("Environnement de travail préféré", ENVIRONNEMENTS)
    metiers = st.multiselect("Type de métier visé (max 2)", METIERS, max_selections=2)
    if agent.os.environ.get("ANTHROPIC_API_KEY"):
        mode = "🔑 LLM Anthropic"
    elif agent.os.environ.get("GEMINI_API_KEY"):
        mode = "🔑 LLM Gemini (gratuit)"
    else:
        mode = "⚙️ Déterministe (sans clé API)"
    st.caption(f"Mode agent : {mode}")

profil = {"serie_bac": serie, "note_maths": note_maths, "note_sciences": note_sciences,
          "note_langues": note_langues, "note_eco": note_eco,
          "matieres_preferees": matieres, "competences": competences, "interets": interets,
          "environnement": environnement, "metiers_vises": metiers}

# ------------------------------------------------------------------ chat
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "contenu":
        "Bonjour ! Je suis ORIENT'IA, l'assistant d'orientation de l'ISPM. Renseignez votre "
        "profil dans la barre latérale, puis posez vos questions : présentation d'une filière, "
        "comparaison, prérequis, recommandation personnalisée…", "meta": None}]

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["contenu"])
        if m.get("meta"):
            meta = m["meta"]
            with st.expander(f"🔍 Traces — {meta['latence_ms']} ms · mode {meta['mode']}"
                             + (f" · REFUS ({meta['refus']})" if meta["refus"] else "")):
                for a in meta["outils"]:
                    st.markdown(f"**Outil `{a['outil']}`**")
                    st.json({"entrée": a["entree"], "sortie": a["sortie"]}, expanded=False)
                if not meta["outils"]:
                    st.caption("Aucun outil appelé (refus de sécurité ou réponse directe).")
                st.caption("Trace complète : dossier traces/ (JSONL).")

if question := st.chat_input("Votre question…"):
    st.session_state.messages.append({"role": "user", "contenu": question, "meta": None})
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        with st.spinner("Analyse en cours…"):
            r = agent.repondre(question, profil)
        st.markdown(r["reponse"])
    st.session_state.messages.append({"role": "assistant", "contenu": r["reponse"],
                                      "meta": {k: r[k] for k in ["outils", "latence_ms", "refus", "mode"]}})
    st.rerun()
