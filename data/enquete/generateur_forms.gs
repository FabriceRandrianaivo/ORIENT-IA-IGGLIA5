/**
 * Générateur du formulaire d'enquête ORIENT'IA — v3 : FORMULAIRE UNIQUE
 *
 * Un seul lien à diffuser. Le répondant choisit « Étudiant » ou « Professionnel »
 * et Google Forms l'aiguille automatiquement vers la bonne section finale.
 * Le tronc commun est formulé au passé (« au moment de choisir vos études ») :
 * valable pour les deux publics, et méthodologiquement plus juste (on mesure
 * le profil au moment du choix d'orientation).
 *
 * Utilisation :
 * 1. https://script.google.com → Nouveau projet → coller ce script
 * 2. Menu déroulant à côté de Exécuter ▶ : sélectionner "creerFormulaireUnique"
 * 3. Exécuter ▶ puis autoriser les permissions (Forms/Drive)
 * 4. Le lien de diffusion s'affiche dans les journaux (Ctrl+Entrée)
 * 5. Vérifier dans le formulaire : Paramètres → pas de collecte d'e-mail,
 *    pas de restriction à l'organisation
 *
 * Recodage après gel : exporter le CSV des réponses puis
 *   python data/enquete/recoder_reponses.py --unique export.csv
 */

function creerFormulaireUnique() {
  const form = FormApp.create("ORIENT'IA — Enquête orientation");
  form.setDescription('Merci de répondre en moins de 5 minutes. Ce questionnaire est anonyme.');
  form.setCollectEmail(false);
  form.setConfirmationMessage('Merci pour votre participation !');

  // ---------- Section 1 : consentement + tronc commun + aiguillage ----------
  form.addSectionHeaderItem().setTitle('Consentement');
  form.addParagraphTextItem().setTitle(TEXTE_CONSENTEMENT).setRequired(false);
  form.addCheckboxItem()
    .setTitle('Consentement (obligatoire)')
    .setChoiceValues(["J'ai lu ce qui précède et j'accepte que mes réponses anonymes soient utilisées dans le cadre de ce projet académique."])
    .setRequired(true);

  form.addSectionHeaderItem().setTitle('Votre profil au moment de choisir vos études');

  form.addMultipleChoiceItem()
    .setTitle('Quelle était votre série de bac ?')
    .setChoiceValues(OPT_SERIES_BAC).setRequired(true);

  form.addCheckboxItem()
    .setTitle('Quelles étaient vos matières préférées au lycée ? (3 max)')
    .setChoiceValues(OPT_MATIERES).setRequired(true);

  form.addGridItem()
    .setTitle('Votre niveau dans ces domaines à la fin du lycée ? (1 = faible → 5 = excellent)')
    .setRows(['Mathématiques', 'Sciences expérimentales', 'Langues et communication', 'Économie-gestion'])
    .setColumns(['1', '2', '3', '4', '5'])
    .setRequired(true);

  form.addCheckboxItem()
    .setTitle('Quelles compétences aviez-vous au moment de choisir vos études supérieures ?')
    .setChoiceValues(OPT_COMPETENCES).setRequired(true);

  form.addCheckboxItem()
    .setTitle("Quels étaient vos centres d'intérêt à cette époque ? (4 max)")
    .setChoiceValues(OPT_INTERETS).setRequired(true);

  form.addParagraphTextItem()
    .setTitle('Aviez-vous déjà réalisé des projets ou activités marquants (club, association, petit business, compétition…) ?')
    .setRequired(false);

  form.addMultipleChoiceItem()
    .setTitle('Quel environnement de travail recherchiez-vous ?')
    .setChoiceValues(OPT_ENVIRONNEMENT).setRequired(true);

  form.addCheckboxItem()
    .setTitle('Quel type de métier visiez-vous ? (2 max)')
    .setChoiceValues(OPT_METIERS).setRequired(true);

  // Question d'aiguillage — les choix sont reliés aux sections plus bas.
  const aiguillage = form.addMultipleChoiceItem()
    .setTitle('Aujourd\'hui, vous êtes… ?')
    .setRequired(true);

  // ---------- Section 2 : étudiants (se termine par Envoyer) ----------
  const pageEtudiants = form.addPageBreakItem().setTitle('Vous êtes étudiant(e)');

  const choixParcours = PARCOURS_ISPM.concat(['Autre établissement — précisez la filière : ___']);
  form.addMultipleChoiceItem()
    .setTitle('Quelle filière / quel parcours suivez-vous actuellement ?')
    .setChoiceValues(choixParcours).setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle("En quelle année d'étude êtes-vous ?")
    .setChoiceValues(['L1', 'L2', 'L3', 'M1', 'M2', 'Diplômé(e) depuis moins de 3 ans'])
    .setRequired(true);

  form.addScaleItem()
    .setTitle('À quel point êtes-vous satisfait(e) de votre choix de filière ?')
    .setBounds(1, 5).setLabels('Pas du tout', 'Très satisfait')
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle("Si c'était à refaire, choisiriez-vous la même filière ?")
    .setChoiceValues(['Oui', 'Non', 'Pas sûr(e)'])
    .setRequired(true);

  // ---------- Section 3 : professionnels ----------
  const pagePros = form.addPageBreakItem().setTitle('Vous êtes professionnel(le)');

  form.addTextItem()
    .setTitle("Quelle filière / quel domaine d'études avez-vous suivi ?")
    .setRequired(true);

  form.addTextItem()
    .setTitle("Quel métier exercez-vous aujourd'hui ?")
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle("Depuis combien d'années travaillez-vous ?")
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

  // ---------- Câblage de l'aiguillage ----------
  aiguillage.setChoices([
    aiguillage.createChoice('Étudiant(e) — ou diplômé(e) depuis peu', pageEtudiants),
    aiguillage.createChoice('Professionnel(le) en activité', pagePros),
  ]);
  // Après la section étudiants, on soumet (on ne continue pas vers la section pros).
  pagePros.setGoToPage(FormApp.PageNavigationType.SUBMIT);

  Logger.log('=== FORMULAIRE UNIQUE ORIENT\'IA ===');
  Logger.log('Lien de diffusion : ' + form.getPublishedUrl());
  Logger.log("Lien d'édition : " + form.getEditUrl());
  Logger.log('\nRappel : Paramètres > vérifier que la collecte d\'e-mail est désactivée et ' +
    'que le formulaire n\'est pas restreint à une organisation.');
  return form;
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
