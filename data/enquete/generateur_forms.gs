/**
 * Générateur automatique des 2 formulaires d'enquête ORIENT'IA — VERSION CORRIGÉE
 * (Formulaire A - Étudiants / Formulaire B - Professionnels)
 *
 * Corrections apportées par rapport à la v1 :
 *   1. PARCOURS_ISPM : liste officielle complète des 16 filières (source :
 *      site ISPM, voir data/registre_sources.csv — src-filieres)
 *   2. Nouvelle question tronc commun : série de bac (variable du modèle ML
 *      et clé de vérification des prérequis officiels)
 *   3. Centres d'intérêt : ajout de « Droit / justice » (nécessaire pour la
 *      filière DTJA, aligné sur le générateur de données synthétiques)
 *
 * Utilisation :
 * 1. Aller sur https://script.google.com → Nouveau projet
 * 2. Coller ce script (remplacer tout le contenu)
 * 3. Dans le menu déroulant à côté de Exécuter ▶, sélectionner
 *    "creerTousLesFormulaires", puis cliquer sur Exécuter
 * 4. Autoriser les permissions (Forms/Drive)
 * 5. Les liens s'affichent dans les journaux d'exécution (Ctrl+Entrée)
 * 6. Vérifier dans Paramètres de chaque formulaire : pas de collecte d'e-mail,
 *    pas de restriction à l'organisation
 *
 * NB : si les formulaires v1 sont déjà DIFFUSÉS, ne pas régénérer — modifier
 * les formulaires existants à la main (mêmes corrections) pour garder les liens.
 */

function creerTousLesFormulaires() {
  const formA = creerFormulaireEtudiants();
  const formB = creerFormulaireProfessionnels();

  Logger.log('=== FORMULAIRE A — Étudiants ===');
  Logger.log('Lien de réponse (à diffuser) : ' + formA.getPublishedUrl());
  Logger.log("Lien d'édition : " + formA.getEditUrl());

  Logger.log('=== FORMULAIRE B — Professionnels ===');
  Logger.log('Lien de réponse (à diffuser) : ' + formB.getPublishedUrl());
  Logger.log("Lien d'édition : " + formB.getEditUrl());

  Logger.log('\nRappel : vérifiez dans Paramètres > Général de chaque formulaire que ' +
    '"Restreindre à [votre organisation]" est décoché.');

  return {
    etudiants: { reponse: formA.getPublishedUrl(), edition: formA.getEditUrl() },
    professionnels: { reponse: formB.getPublishedUrl(), edition: formB.getEditUrl() }
  };
}

// Liste officielle des 16 filières ISPM (src-filieres, consulté le 26/08/2026)
const PARCOURS_ISPM = [
  'IGGLIA — Informatique de Gestion, Génie Logiciel et IA',
  'ESIIA — Électronique, Systèmes Informatiques et IA',
  'IMTICIA — Informatique, Multimédia, TIC et IA',
  'ISAIA — Informatique, Statistique Appliquée et IA',
  'CAA — Commerce et Administration des Affaires',
  'FIC — Finances et Comptabilités',
  'DTJA — Droit et Techniques Juridiques des Affaires',
  'EMP — Économie et Management de Projet',
  'IAA — Industries Agroalimentaires',
  'PIP — Pharmacologie et Industries Pharmaceutiques',
  'AEE — Agriculture et Élevage',
  'EMII — Électromécanique et Informatique Industrielle',
  'GCA — Génie Civil et Architecture',
  'ICMP — Industries Chimiques, Minières et Pétrolières',
  'TEE — Tourisme et Environnement',
  'TEH — Tourisme et Hôtellerie'
];

const OPT_SERIES_BAC = ['A1', 'A2', 'C', 'D', 'S', 'L',
  'Technique industrielle', 'Technique génie civil', 'Technique agricole', 'Autre'];

const TEXTE_CONSENTEMENT =
  "Ce questionnaire est réalisé par des étudiants de Master 2 de l'ISPM dans le cadre " +
  "d'un examen académique (projet ORIENT'IA, un assistant d'aide à l'orientation).\n\n" +
  "Il est entièrement anonyme : aucun nom, e-mail ou numéro de téléphone n'est collecté. " +
  "Vos réponses seront utilisées uniquement dans le cadre de ce projet, sous forme " +
  "anonymisée. Vous pouvez arrêter de répondre à tout moment. Répondre prend moins de 5 minutes.";

const OPT_MATIERES = ['Mathématiques', 'Physique-Chimie', 'SVT', 'Informatique / Technologie',
  'Français / Littérature', 'Langues étrangères', 'Histoire-Géographie', 'Économie / Gestion', 'Arts', 'Sport'];
const OPT_COMPETENCES = ['Programmation', 'Analyse de données / logique', 'Rédaction / communication',
  'Créativité / design', 'Organisation / gestion de projet', 'Vente / négociation',
  'Électronique / bricolage technique', 'Travail en équipe', 'Autre'];
const OPT_INTERETS = ['Technologie / informatique', 'Sciences', 'Entrepreneuriat / business',
  'Finance / comptabilité', 'Art / design / audiovisuel', 'Communication / médias',
  'Tourisme / hôtellerie', 'Agriculture / environnement', 'BTP / construction',
  'Santé / social', 'Droit / justice', 'Autre'];
const OPT_ENVIRONNEMENT = ['Bureau', 'Terrain / extérieur', 'Laboratoire', 'Atelier / usine', 'Mixte / peu importe'];
const OPT_METIERS = ['Technique / ingénierie', 'Gestion / management', 'Création / design',
  'Commerce / relation client', 'Recherche / enseignement', 'Entrepreneur / indépendant', 'Je ne sais pas encore'];

function ajouterConsentement(form) {
  form.addSectionHeaderItem().setTitle('Consentement');
  form.addParagraphTextItem().setTitle(TEXTE_CONSENTEMENT).setRequired(false);
  form.addCheckboxItem()
    .setTitle('Consentement (obligatoire)')
    .setChoiceValues(["J'ai lu ce qui précède et j'accepte que mes réponses anonymes soient utilisées dans le cadre de ce projet académique."])
    .setRequired(true);
}

function ajouterTroncCommun(form, auPasse) {
  const v = auPasse ? {
    q0: 'Quelle était votre série de bac ?',
    q1: 'Quelles étaient vos matières préférées au lycée ?',
    q2: 'Votre niveau dans ces domaines à la fin du lycée ?',
    q3: 'Quelles compétences aviez-vous déjà avant vos études supérieures ?',
    q4: "Quels étaient vos centres d'intérêt à l'époque ?",
    q5: 'Aviez-vous réalisé des projets ou activités marquants avant vos études ?',
    q6: 'Quel environnement de travail recherchiez-vous ?',
    q7: "Quel type de métier visiez-vous à l'époque ?"
  } : {
    q0: 'Quelle était ta série de bac ?',
    q1: 'Quelles étaient tes matières préférées au lycée ?',
    q2: 'Comment évalues-tu ton niveau dans ces domaines à la fin du lycée ?',
    q3: 'Quelles compétences estimes-tu avoir ?',
    q4: "Quels sont tes centres d'intérêt ?",
    q5: 'As-tu déjà réalisé des projets ou activités marquants (club, association, petit business, projet perso, compétition…) ?',
    q6: 'Quel environnement de travail préfères-tu ?',
    q7: 'Quel type de métier vises-tu ?'
  };

  form.addSectionHeaderItem().setTitle('Tronc commun');

  // Série de bac : variable du modèle + clé des prérequis officiels
  form.addMultipleChoiceItem().setTitle(v.q0).setChoiceValues(OPT_SERIES_BAC).setRequired(true);

  form.addCheckboxItem().setTitle(v.q1 + ' (3 max)').setChoiceValues(OPT_MATIERES).setRequired(true);

  form.addGridItem().setTitle(v.q2 + ' (1 = faible → 5 = excellent)')
    .setRows(['Mathématiques', 'Sciences expérimentales', 'Langues et communication', 'Économie-gestion'])
    .setColumns(['1', '2', '3', '4', '5'])
    .setRequired(true);

  form.addCheckboxItem().setTitle(v.q3).setChoiceValues(OPT_COMPETENCES).setRequired(true);
  form.addCheckboxItem().setTitle(v.q4 + ' (4 max)').setChoiceValues(OPT_INTERETS).setRequired(true);
  form.addParagraphTextItem().setTitle(v.q5).setRequired(false);
  form.addMultipleChoiceItem().setTitle(v.q6).setChoiceValues(OPT_ENVIRONNEMENT).setRequired(true);
  form.addCheckboxItem().setTitle(v.q7 + ' (2 max)').setChoiceValues(OPT_METIERS).setRequired(true);
}

function creerFormulaireEtudiants() {
  const form = FormApp.create("ORIENT'IA — Enquête étudiants");
  form.setDescription('Merci de répondre en moins de 5 minutes. Ce questionnaire est anonyme.');
  form.setCollectEmail(false);
  form.setConfirmationMessage('Merci pour ta participation !');

  ajouterConsentement(form);
  ajouterTroncCommun(form, false);

  form.addSectionHeaderItem().setTitle('Spécifique étudiants');

  const choixParcours = PARCOURS_ISPM.concat(['Autre établissement — précise la filière : ___']);
  form.addMultipleChoiceItem()
    .setTitle('Quelle filière / quel parcours suis-tu actuellement ?')
    .setChoiceValues(choixParcours)
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle("En quelle année d'étude es-tu ?")
    .setChoiceValues(['L1', 'L2', 'L3', 'M1', 'M2', 'Diplômé(e) depuis moins de 3 ans'])
    .setRequired(true);

  form.addScaleItem()
    .setTitle('À quel point es-tu satisfait(e) de ton choix de filière ?')
    .setBounds(1, 5).setLabels('Pas du tout', 'Très satisfait')
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle("Si c'était à refaire, choisirais-tu la même filière ?")
    .setChoiceValues(['Oui', 'Non', 'Pas sûr(e)'])
    .setRequired(true);

  return form;
}

function creerFormulaireProfessionnels() {
  const form = FormApp.create("ORIENT'IA — Enquête professionnels");
  form.setDescription('Merci de répondre en moins de 5 minutes. Ce questionnaire est anonyme.');
  form.setCollectEmail(false);
  form.setConfirmationMessage('Merci pour votre participation !');

  ajouterConsentement(form);
  ajouterTroncCommun(form, true);

  form.addSectionHeaderItem().setTitle('Spécifique professionnels');

  form.addTextItem()
    .setTitle("Quelle filière / quel domaine d'études avez-vous suivi ?")
    .setRequired(true);

  form.addTextItem()
    .setTitle("Quel métier exercez-vous aujourd'hui ?")
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle('Depuis combien d\'années travaillez-vous ?')
    .setChoiceValues(['Moins de 3 ans', '3 à 7 ans', '8 à 15 ans', 'Plus de 15 ans'])
    .setRequired(true);

  form.addScaleItem()
    .setTitle('Avec le recul, votre formation était-elle adaptée au métier que vous exercez ?')
    .setBounds(1, 5).setLabels('Pas du tout', 'Parfaitement')
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle('Avec le recul, auriez-vous choisi une autre filière ?')
    .setChoiceValues(['Non, le même choix', 'Oui — laquelle : ___', 'Pas sûr(e)'])
    .setRequired(true);

  return form;
}
