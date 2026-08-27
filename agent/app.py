"""Interface ORIENT'IA (Streamlit) — design "Plateforme d'Orientation".

Lancement :  streamlit run agent/app.py
Le profil est DECLARE par l'utilisateur (barre laterale OU mini-formulaire dans
le chat) ; l'assistant n'infere rien. Chaque reponse expose ses traces et la
mention obligatoire est affichee en permanence (exigences du sujet).
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

st.set_page_config(page_title="ORIENT'IA — Dashboard d'Orientation", page_icon="🎓",
                   layout="wide", initial_sidebar_state="expanded")

# ------------------------------------------------------------------ styles
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@500;600;700;800&family=Public+Sans:wght@400;500;600&display=swap');

  :root {
    --vert-nuit: #0b3d2b; --vert: #14603f; --vert-vif: #1e7a4f;
    --menthe: #bff0d4; --fond: #eef2ee; --carte: #ffffff; --ligne: #dfe7e1;
  }
  html, body, [class*="css"] { font-family: 'Public Sans', 'Segoe UI', sans-serif; }
  h1, h2, h3 { font-family: 'Outfit', sans-serif; }
  .stApp { background: var(--fond); }
  .block-container { padding-top: 0.4rem; max-width: 64rem; }
  #MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }

  /* ---------- navbar superieure ---------- */
  .topnav {
    background: var(--vert-nuit); border-radius: 0 0 14px 14px;
    display: flex; align-items: center; justify-content: space-between;
    padding: 12px 22px; margin: 0 0 14px;
  }
  .topnav .brand { color: #fff; font-family: 'Outfit'; font-weight: 800; font-size: 1.05rem; letter-spacing: .02em; }
  .topnav .links a {
    color: #cfe8d9; text-decoration: none; font-size: .78rem; font-weight: 600;
    margin-left: 18px;
  }
  .topnav .links a:hover { color: #ffffff; }

  /* ---------- hero ---------- */
  .hero {
    position: relative; overflow: hidden;
    background: linear-gradient(100deg, var(--vert-nuit) 0%, var(--vert) 80%);
    border-radius: 18px; padding: 26px 30px; color: #fff; margin-bottom: 14px;
    box-shadow: 0 10px 28px rgba(11, 61, 43, .25);
  }
  .hero::after {
    content: ""; position: absolute; right: 26px; top: 50%; transform: translateY(-50%);
    width: 150px; height: 150px; border-radius: 50%;
    background: linear-gradient(135deg, rgba(255,255,255,.16), rgba(255,255,255,.05));
  }
  .hero h1 { color: #fff; font-size: 2.1rem; font-weight: 800; margin: 0; display: inline; vertical-align: middle; }
  .hero .cap { font-size: 1.7rem; vertical-align: middle; margin-right: 8px; }
  .hero .tagline { color: #cfe8d9; margin: 6px 0 14px; font-size: .95rem; }
  .hero .chips span {
    background: rgba(255,255,255,.13); border: 1px solid rgba(255,255,255,.28);
    color: #eaf6ef; font-size: .72rem; font-weight: 600; padding: 5px 14px;
    border-radius: 999px; margin-right: 8px;
  }

  /* ---------- stepper ---------- */
  .stepper {
    background: var(--carte); border: 1px solid var(--ligne); border-radius: 16px;
    display: flex; align-items: center; padding: 16px 26px; margin-bottom: 12px;
    box-shadow: 0 3px 12px rgba(31, 60, 43, .05);
  }
  .step { display: flex; flex-direction: column; align-items: center; gap: 6px; min-width: 130px; }
  .step .dot {
    width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center;
    justify-content: center; font-weight: 700; font-size: .85rem;
    background: #e6ede8; color: #7d8a80; border: 2px solid var(--ligne);
  }
  .step.on .dot { background: var(--vert-vif); color: #fff; border-color: var(--vert-vif); }
  .step .lbl { font-size: .74rem; font-weight: 700; color: #2c4636; text-align: center; }
  .step .sub { font-size: .64rem; color: #7d8a80; text-align: center; margin-top: -4px; }
  .lien { flex: 1; height: 2px; background: var(--ligne); margin: 0 10px 26px; }
  .lien.on { background: var(--vert-vif); }

  /* ---------- bandeau mention ---------- */
  .mention {
    background: #dff0e5; border: 1px solid #c4e2d0; border-radius: 12px;
    padding: 10px 16px; font-size: .8rem; color: #24523a; margin-bottom: 16px;
  }

  /* ---------- cartes filieres ---------- */
  .carte-filiere {
    background: var(--carte); border: 1.5px solid var(--ligne); border-radius: 14px;
    padding: 13px 15px 11px; height: 100%;
    box-shadow: 0 3px 12px rgba(31, 60, 43, .07);
  }
  .carte-filiere.premiere { border-color: var(--vert-vif); background: linear-gradient(180deg, #eaf5ee 0%, #ffffff 55%); }
  .carte-filiere .rang {
    display: inline-block; font-size: .62rem; font-weight: 700; letter-spacing: .05em;
    color: #7d8a80; margin-bottom: 4px;
  }
  .carte-filiere.premiere .rang {
    background: var(--vert-vif); color: #fff; border-radius: 999px; padding: 2px 10px;
  }
  .carte-filiere .sigle { font-family: 'Outfit'; font-size: 1.22rem; font-weight: 800; color: #14321f; }
  .carte-filiere .nom { font-size: .72rem; color: #5b6459; line-height: 1.35; min-height: 2.6em; }
  .carte-filiere .barre { height: 7px; background: #e2eae4; border-radius: 99px; overflow: hidden; margin-top: 8px; }
  .carte-filiere .barre div { height: 100%; background: linear-gradient(90deg, var(--vert), var(--vert-vif)); }
  .carte-filiere .pct { font-family: 'Outfit'; font-weight: 800; color: var(--vert-vif); font-size: .95rem; text-align: right; }

  /* ---------- chat ---------- */
  [data-testid="stChatMessage"] {
    border-radius: 16px; padding: 15px 18px; margin-bottom: 12px;
    border: 1px solid var(--ligne); background: var(--carte);
    box-shadow: 0 2px 10px rgba(31, 60, 43, .05);
  }
  [data-testid="stChatInput"] {
    border-radius: 999px; border: 1.5px solid #d3e4d9; background: #fff;
    box-shadow: 0 4px 16px rgba(31, 60, 43, .08);
  }
  [data-testid="stChatInput"]:focus-within { border-color: var(--vert-vif); }

  /* ---------- sidebar ---------- */
  [data-testid="stSidebar"] { background: linear-gradient(180deg, var(--vert-nuit) 0%, #114a33 100%); }
  [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #fff; font-family: 'Outfit'; }
  [data-testid="stSidebar"] label p, [data-testid="stSidebar"] .stMarkdown p,
  [data-testid="stSidebar"] [data-testid="stCaptionContainer"],
  [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
  [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p { color: #d9e8de !important; }
  [data-testid="stSidebar"] [data-testid="stExpander"] {
    background: rgba(255,255,255,.07); border-radius: 12px; border: 1px solid rgba(255,255,255,.18);
  }
  [data-testid="stSidebar"] [data-testid="stExpander"] summary p,
  [data-testid="stSidebar"] [data-testid="stExpander"] summary span { color: #e8f2ec !important; }
  [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.2); }
  span[data-baseweb="tag"] { background: var(--vert) !important; border-radius: 999px; }

  .logo-bloc { text-align: center; padding: 6px 0 2px; }
  .logo-bloc .rond {
    width: 58px; height: 58px; border-radius: 50%; background: #fff; margin: 0 auto 8px;
    display: flex; align-items: center; justify-content: center; font-size: 1.7rem;
    box-shadow: 0 4px 14px rgba(0,0,0,.25);
  }
  .logo-bloc .titre { color: #fff; font-family: 'Outfit'; font-weight: 800; font-size: 1.05rem; letter-spacing: .03em; }
  .logo-bloc .sous { color: #9fc4ae; font-size: .68rem; }
  .nav-item {
    display: flex; align-items: center; gap: 10px; color: #cfe8d9;
    font-size: .8rem; font-weight: 600; padding: 8px 12px; border-radius: 10px; margin: 2px 0;
  }
  .nav-item.actif { background: var(--vert-vif); color: #fff; }

  /* ---------- boutons ---------- */
  .stButton button {
    border: 1.5px solid var(--vert); color: #145032; background: #ffffff;
    border-radius: 999px; font-size: .8rem; font-weight: 700; padding: 7px 16px;
    transition: all .15s ease;
  }
  .stButton button:hover:enabled {
    background: var(--vert); color: #fff; transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(20, 96, 63, .3);
  }
  .stButton button:disabled { opacity: .45; }
  [data-testid="stSidebar"] .stButton button[kind="primary"],
  [data-testid="stSidebar"] .stButton button[data-testid="stBaseButton-primary"] {
    background: #ffffff; color: #0b3d2b; border-color: #ffffff;
  }
  [data-testid="stSidebar"] .stButton button[kind="secondary"] {
    background: var(--menthe); color: #0b3d2b; border-color: var(--menthe);
  }

  .footer-note {
    text-align: center; color: #7d8a80; font-size: .7rem;
    margin-top: 22px; padding-top: 12px; border-top: 1px solid var(--ligne);
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
    st.session_state.messages.append({"role": "assistant", "contenu": r["reponse"],
                                      "meta": {k: r[k] for k in ["outils", "latence_ms", "refus", "mode"]}})


# ----------------------------------------------------------- barre laterale
with st.sidebar:
    st.markdown("""
    <div class="logo-bloc">
      <div class="rond">🎓</div>
      <div class="titre">ORIENT'IA</div>
      <div class="sous">Plateforme d'Orientation</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="nav-item actif">👤&nbsp; Mon Profil</div>', unsafe_allow_html=True)

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

    remplis = sum(bool(v) for v in [serie, matieres, interets, competences, environnement, metiers])
    st.progress(remplis / 6, text=f"Profil : {remplis}/6")
    pret = bool(serie and matieres and interets)
    if not pret:
        manques = [n for n, v in [("série de bac", serie), ("matières", matieres),
                                  ("intérêts", interets)] if not v]
        st.caption("✏️ Il manque : " + ", ".join(manques))

    with st.expander("🎓 Parcours (16 filières)"):
        for m_nom, sigles_m in tools._FORMATIONS["mentions_lmd"]["mentions"].items():
            st.caption(m_nom)
            for s in sigles_m:
                st.markdown(f"{EMOJI_FILIERE.get(s, '🎓')} **{s}** — "
                            f"<small>{tools._PAR_SIGLE[s]['nom']}</small>", unsafe_allow_html=True)
    with st.expander("📚 Ressources (sources officielles)"):
        for sid, r in _registre_sources().items():
            st.caption(f"[{sid}] {r['titre']} — {r['statut']}, {r['date_consultation']}")

    st.divider()
    if st.button("🧭 Obtenir ma recommandation", type="primary",
                 use_container_width=True, disabled=not pret):
        traiter("Quels parcours me correspondent ?")
        st.rerun()
    if st.button("＋ Nouvelle Session", type="secondary", use_container_width=True):
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
<div class="topnav">
  <span class="brand">ORIENT'IA</span>
  <span class="links">
    <a href="https://ispm-edu.com" target="_blank">Site ISPM</a>
    <a href="mailto:contact@ispm.education">Contact</a>
  </span>
</div>
<div class="hero">
  <span class="cap">🎓</span><h1>ORIENT'IA</h1>
  <p class="tagline">Assistant intelligent d'orientation — 16 filières</p>
  <div class="chips"><span>◉ Sources officielles citées</span><span>☑ 38/38 tests</span>
  <span>◈ Modèle ML expliqué</span></div>
</div>
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


# ---------------------------------------------------------------- rendu chat
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
