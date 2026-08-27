"""Interface ORIENT'IA (Streamlit).

Lancement :  streamlit run agent/app.py
Le profil est DECLARE par l'utilisateur dans la barre laterale (collecte
progressive) ; l'assistant n'infere rien. Chaque reponse expose ses traces
(outils appeles, scores, latence) et la mention obligatoire est affichee en
permanence (exigences du sujet).
"""

import csv
import re
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

st.set_page_config(page_title="ORIENT'IA — ISPM", page_icon="🎓", layout="wide",
                   initial_sidebar_state="expanded")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@500;600;700&family=Public+Sans:wght@400;500;600&display=swap');

  html, body, [class*="css"] { font-family: 'Public Sans', 'Segoe UI', sans-serif; }
  h1, h2, h3 { font-family: 'Outfit', 'Segoe UI', sans-serif; }
  .block-container { padding-top: 1.2rem; max-width: 62rem; }
  #MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }

  .orientia-hero {
    position: relative; overflow: hidden;
    background: linear-gradient(115deg, #0d3b23 0%, #1e6b45 55%, #2e8a5c 100%);
    border-radius: 16px; padding: 22px 28px 18px; color: #ffffff;
    box-shadow: 0 8px 26px rgba(13, 59, 35, .22);
  }
  .orientia-hero::before {
    content: ""; position: absolute; right: -60px; top: -60px; width: 240px; height: 240px;
    background: radial-gradient(circle, rgba(255,255,255,.14) 0%, transparent 65%);
  }
  .orientia-hero h1 { color: #fff; font-size: 1.9rem; font-weight: 700; margin: 0; display: inline; }
  .orientia-hero .tagline { color: #cfe8d9; margin: 4px 0 0; font-size: .9rem; }

  .etapes { display: flex; flex-wrap: wrap; gap: 10px; margin: 14px 0 4px; }
  .etape {
    flex: 1; min-width: 180px; display: flex; align-items: center; gap: 10px;
    background: #ffffff; border: 1.5px solid #dfe7e1; border-radius: 12px; padding: 10px 14px;
  }
  .etape.ok { border-color: #1e6b45; background: #eaf3ed; }
  .etape .num {
    width: 26px; height: 26px; border-radius: 50%; flex: none;
    display: flex; align-items: center; justify-content: center;
    background: #dfe7e1; color: #5b6459; font-weight: 700; font-size: .85rem;
  }
  .etape.ok .num { background: #1e6b45; color: #fff; }
  .etape .lbl { font-size: .82rem; line-height: 1.3; color: #2c4636; }
  .etape .lbl b { display: block; font-size: .86rem; color: #14321f; }

  .mention {
    background: #eef5f0; border: 1px solid #d5e5da; border-left: 5px solid #1e6b45;
    border-radius: 0 10px 10px 0; padding: 8px 14px; font-size: .8rem;
    color: #2c4636; margin: 10px 0 16px;
  }

  .carte-filiere {
    background: #ffffff; border: 1.5px solid #d3e4d9; border-radius: 14px;
    padding: 14px 16px 12px; height: 100%;
    box-shadow: 0 3px 12px rgba(31, 60, 43, .07);
  }
  .carte-filiere.premiere { border-color: #1e6b45; background: linear-gradient(180deg, #eaf3ed 0%, #ffffff 60%); }
  .carte-filiere .rang { font-size: .68rem; font-weight: 700; letter-spacing: .06em; color: #7d8a80; }
  .carte-filiere.premiere .rang { color: #1e6b45; }
  .carte-filiere .sigle { font-family: 'Outfit'; font-size: 1.25rem; font-weight: 700; color: #14321f; margin: 2px 0; }
  .carte-filiere .nom { font-size: .74rem; color: #5b6459; line-height: 1.35; min-height: 2.6em; }
  .carte-filiere .barre { height: 8px; background: #e2eae4; border-radius: 99px; overflow: hidden; margin-top: 8px; }
  .carte-filiere .barre div { height: 100%; background: linear-gradient(90deg, #1e6b45, #2e8a5c); border-radius: 99px; }
  .carte-filiere .pct { font-family: 'Outfit'; font-weight: 700; color: #1e6b45; font-size: .95rem; margin-top: 4px; }

  [data-testid="stChatMessage"] {
    border-radius: 18px; padding: 15px 18px; margin-bottom: 12px;
    border: 1px solid #e2eae4; background: #ffffff;
    box-shadow: 0 3px 14px rgba(31, 60, 43, .06);
  }

  /* --- Barre laterale sombre (inspiration myAuxilium, en vert ISPM) --- */
  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a2b19 0%, #10402a 70%, #14603a 100%);
  }
  [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: #ffffff; font-family: 'Outfit';
  }
  [data-testid="stSidebar"] label p,
  [data-testid="stSidebar"] .stMarkdown p,
  [data-testid="stSidebar"] [data-testid="stCaptionContainer"],
  [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
  [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
    color: #d9e8de !important;
  }
  [data-testid="stSidebar"] [data-testid="stExpander"] {
    background: rgba(255, 255, 255, .07); border-radius: 14px;
    border: 1px solid rgba(255, 255, 255, .18);
  }
  [data-testid="stSidebar"] [data-testid="stExpander"] summary p,
  [data-testid="stSidebar"] [data-testid="stExpander"] summary span {
    color: #e8f2ec !important;
  }
  [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.2); }
  span[data-baseweb="tag"] { background: #1e6b45 !important; border-radius: 999px; }
  [data-testid="stSidebar"] .stButton button {
    background: rgba(255,255,255,.10); color: #eaf6ef; border-color: rgba(255,255,255,.35);
  }
  [data-testid="stSidebar"] .stButton button:hover:enabled {
    background: #ffffff; color: #14321f; border-color: #ffffff;
  }
  [data-testid="stSidebar"] .stButton button[kind="primary"],
  [data-testid="stSidebar"] .stButton button[data-testid="stBaseButton-primary"] {
    background: #2e8a5c; color: #ffffff; border-color: #2e8a5c;
  }

  /* Zone de saisie facon pill */
  [data-testid="stChatInput"] {
    border-radius: 999px; border: 1.5px solid #d3e4d9;
    box-shadow: 0 4px 16px rgba(31, 60, 43, .08);
  }
  [data-testid="stChatInput"]:focus-within { border-color: #1e6b45; }

  .stButton button {
    border: 1.5px solid #1e6b45; color: #145032; background: #ffffff;
    border-radius: 999px; font-size: .82rem; font-weight: 600; padding: 6px 15px;
    transition: all .15s ease;
  }
  .stButton button:hover:enabled {
    background: #1e6b45; color: #ffffff;
    transform: translateY(-1px); box-shadow: 0 4px 12px rgba(30, 107, 69, .30);
  }
  .stButton button[kind="primary"], .stButton button[data-testid="stBaseButton-primary"] {
    background: #1e6b45; color: #ffffff; border-color: #1e6b45; font-size: .9rem; padding: 9px 15px;
  }
  .stButton button:disabled { opacity: .45; }

  .footer-note {
    text-align: center; color: #7d8a80; font-size: .72rem;
    margin-top: 24px; padding-top: 12px; border-top: 1px solid #e2eae4;
  }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------- etat
if "messages" not in st.session_state:
    st.session_state.messages = []


@st.cache_data
def _registre_sources() -> dict:
    chemin = Path(__file__).resolve().parents[1] / "data" / "registre_sources.csv"
    with open(chemin, encoding="utf-8") as fh:
        return {r["id"]: r for r in csv.DictReader(fh)}


def afficher_sources(texte: str):
    """Panneau Sources : détail du registre pour chaque [src-…] cité."""
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
    """Questions exploratoires contextuelles proposées après chaque réponse."""
    outils = [a["outil"] for a in meta["outils"]] if meta else []
    if meta and meta.get("refus"):
        return ["Quels parcours me correspondent ?",
                "Cette recommandation repose-t-elle sur des données réelles ou générées ?"]
    for a in (meta["outils"] if meta else []):
        if a["outil"] == "analyser_profil_ml" and "top3" in a.get("sortie", {}):
            s = [t["sigle"] for t in a["sortie"]["top3"]]
            return [f"Pourquoi ton modèle recommande-t-il ce parcours ?",
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
    st.session_state.messages.append({"role": "assistant", "contenu": r["reponse"],
                                      "meta": {k: r[k] for k in ["outils", "latence_ms", "refus", "mode"]}})


# ----------------------------------------------------------- profil declare
with st.sidebar:
    st.header("👤 Étape 1 — Mon profil")
    st.caption("L'assistant n'utilise que ce que vous déclarez ici — jamais votre style d'écriture.")

    serie = st.selectbox("🎯 Série de bac *", [""] + tools.SERIES, key="k_serie",
                         help="Obligatoire : détermine les filières accessibles")
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
              "matieres_preferees": matieres, "competences": competences, "interets": interets,
              "environnement": environnement, "metiers_vises": metiers}

    pret = bool(serie and matieres and interets)
    if pret:
        st.success("Profil prêt ✔", icon="✅")
    else:
        manques = [n for n, v in [("série de bac", serie), ("matières", matieres),
                                  ("intérêts", interets)] if not v]
        st.warning("Il manque : " + ", ".join(manques), icon="✏️")

    if st.button("🧭 Obtenir ma recommandation", type="primary",
                 use_container_width=True, disabled=not pret):
        traiter("Quels parcours me correspondent ?")
        st.rerun()

    st.divider()
    if st.button("🧹 Nouvelle conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    if agent.os.environ.get("ANTHROPIC_API_KEY"):
        st.caption("Mode agent : 🔑 LLM Anthropic")
    elif agent.os.environ.get("GEMINI_API_KEY"):
        st.caption("Mode agent : 🔑 LLM Gemini (gratuit)")
    elif agent.os.environ.get("GROQ_API_KEY"):
        st.caption("Mode agent : 🔑 LLM Groq (gratuit)")
    else:
        st.caption("Mode agent : ⚙️ Déterministe · 100 % local")

# Le mini-formulaire de profil integre au chat vient d'etre valide :
# relancer la recommandation avec le profil mis a jour.
if st.session_state.pop("auto_reco", False):
    traiter("Quels parcours me correspondent ?")

# ------------------------------------------------------------------- entete
a_pose_question = any(m["role"] == "user" for m in st.session_state.messages)
a_recommandation = any(m.get("meta") and any(o["outil"] == "analyser_profil_ml"
                                             for o in m["meta"]["outils"])
                       for m in st.session_state.messages if m.get("meta"))

st.markdown(f"""
<div class="orientia-hero">
  <h1>🎓 ORIENT'IA</h1>
  <p class="tagline">Assistant intelligent d'orientation — Institut Supérieur Polytechnique de Madagascar · 16 filières</p>
</div>
<div class="etapes">
  <div class="etape {'ok' if pret else ''}">
    <div class="num">{'✓' if pret else '1'}</div>
    <div class="lbl"><b>Remplir mon profil</b>dans le panneau de gauche 👈</div>
  </div>
  <div class="etape {'ok' if a_pose_question else ''}">
    <div class="num">{'✓' if a_pose_question else '2'}</div>
    <div class="lbl"><b>Poser une question</b>ou cliquer « Obtenir ma recommandation »</div>
  </div>
  <div class="etape {'ok' if a_recommandation else ''}">
    <div class="num">{'✓' if a_recommandation else '3'}</div>
    <div class="lbl"><b>Explorer les résultats</b>top 3, sources citées, traces</div>
  </div>
</div>
<div class="mention">ℹ️ ORIENT'IA constitue un outil d'aide à l'orientation. Ses recommandations ne
remplacent ni l'avis d'un conseiller pédagogique ni une décision officielle d'admission.</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------- rendu chat
def cartes_top3(meta):
    """Si la reponse contient un appel au modele ML, affiche le top-3 en cartes."""
    for a in meta["outils"]:
        if a["outil"] == "analyser_profil_ml" and "top3" in a.get("sortie", {}):
            top3 = a["sortie"]["top3"]
            colonnes = st.columns(len(top3))
            for i, (col, t) in enumerate(zip(colonnes, top3)):
                pct = round(t["probabilite"] * 100)
                col.markdown(f"""
<div class="carte-filiere {'premiere' if i == 0 else ''}">
  <div class="rang">{'🥇 MEILLEURE CORRESPONDANCE' if i == 0 else f'#{i + 1}'}</div>
  <div class="sigle">{EMOJI_FILIERE.get(t['sigle'], '🎓')} {t['sigle']}</div>
  <div class="nom">{t['nom']}</div>
  <div class="barre"><div style="width:{max(pct, 3)}%"></div></div>
  <div class="pct">{pct} %</div>
</div>""", unsafe_allow_html=True)
            return


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

# Questions exploratoires contextuelles apres la derniere reponse,
# sinon suggestions de depart.
# Collecte progressive DANS le chat (exigence « recueillir progressivement ») :
# quand l'assistant demande le profil, un mini-formulaire apparait dans la
# conversation — l'utilisateur repond a l'IA sans passer par la barre laterale.
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

st.markdown('<div class="footer-note">Prototype académique — Examen de fin d\'études M2, ISPM · '
            'Données : site officiel + brochure août 2025 · Traces complètes dans traces/ (JSONL)</div>',
            unsafe_allow_html=True)
