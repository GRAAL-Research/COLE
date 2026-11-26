# Cadrage : COLE, site statique et refonte

Statut : brouillon à valider. Date : 2026-11-26.

## Solution ancrée (mise de côté, réévaluée à la fin)

« Un site statique sur GitHub Pages, sans dépôt de résultats, avec un classement
refait et une page de vulgarisation à trois niveaux. »

## Problème

Une personne qui veut savoir quel modèle de langage est fiable en français
québécois ouvre colebenchmark.org et trouve un tableau de 96 entrées sur 27
colonnes (nom, score composite et 25 colonnes de métrique : 23 tâches, dont
fquad et piaf qui portent deux métriques chacune), lisible seulement par un
spécialiste. La page ne montre ni la date d'évaluation, ni le coût, ni la
taille (la taille existe dans `predictions/llm_details.csv` mais n'est pas
affichée), ni ce que mesure chaque colonne.

Les modèles récents manquent. Le classement en ligne (`leaderboard.json`, 96
entrées) ne contient que 2 Claude (Opus 4 et Sonnet 4, mai 2025) et 2 Cohere
(aya-expanse-8b, aya-23-8b). Dix-neuf modèles configurés dans
`predictions/all_llms.py` en sont absents (dont Claude Sonnet 4.5, Haiku 4.5,
Opus 4.1, GPT-5.1, Gemini 3 Pro, Command A). Les familles Claude 5 et Cohere
2026 ne sont pas encore dans le dépôt : elles viennent du registre du projet
Tribune (fleet_private.json, fleet_cohere.json). Deux sources divergent :
`predictions/results/full_results_table.csv` (article) contient déjà
Claude-sonnet-4-5 et GPT-5, que `leaderboard.json` n'a pas. La source de
vérité retenue sera le registre de modèles décrit plus bas.

Pourquoi ce n'est pas résolu : le site est né comme annexe d'un article, avec un
backend FastAPI à entretenir sur HuggingFace, un protocole d'évaluation qui
fausse des résultats (dans `open_ai_api_lm_wrapper.py` : une relance réussie
renvoie None donc NA, des `except` nus confondent refus, 429 et délai dépassé,
un `eval()` est appliqué à la sortie du modèle, et les branches testées dans
l'ordre « 0 » avant « 10 » et « 11 » rendent ces deux étiquettes
inatteignables) et aucun processus pour ajouter un modèle.

En quoi nous sommes une partie du problème : l'ajout d'un modèle dépend d'une
personne et d'une soumission manuelle ; le public a été invité à déposer des
résultats que personne ne peut vérifier.

## Publics (arbitrage si deux besoins s'opposent, dans cet ordre)

1. Praticiens et entreprises qui choisissent un modèle (niveau 2).
2. Grand public, médias, étudiants (niveau 1).
3. Fournisseurs de modèles (veulent leur rang, demandent une évaluation).
Les chercheurs en NLP restent servis par le niveau 3, mais ne priment pas.

## Jobs to be done

- Praticien : quand je dois choisir un LLM pour des textes en français du
  Québec, je veux comparer quelques modèles par type de tâche avec leur coût et
  leur taille, afin de justifier mon choix devant mon équipe.
- Grand public : quand j'entends parler d'un classement des IA en français, je
  veux comprendre en une minute ce qu'il mesure et ce que ça change, afin de ne
  pas répéter un chiffre que je ne comprends pas.
- Fournisseur : quand mon modèle sort, je veux savoir comment il se compare et
  comment le faire évaluer, afin de le situer sans fabriquer mes propres tests.

## Résultat visé

Les valeurs « aujourd'hui » sont celles mesurées dans le dépôt le 2026-11-26.
Il n'existe aucune mesure d'audience (décision : on n'en ajoute pas), donc
aucune métrique d'usage chiffrée n'est possible ; l'usage se juge sur des
preuves qualitatives (voir plus bas).

| Métrique | Aujourd'hui | Cible | Échéance |
|---|---|---|---|
| Couverture du registre : modèles du registre (`models.yaml`) évalués en v2 | 0 sur 19 modèles de `all_llms.py` absents, plus la famille Claude 5 et les Cohere 2026 | 100 % des modèles du registre | 3 mois après la mise en ligne |
| Fraîcheur : délai entre la sortie d'un modèle du registre et son entrée au classement | non suivi | moins de 30 jours (sans engagement envers un fournisseur) | régime permanent, relevé tous les trimestres |
| Décision d'un praticien : sur 5 praticiens nommés, nombre qui choisissent un modèle plausible entre 2 candidats en moins de 3 minutes avec la page niveau 2 | non mesuré | 4 sur 5, avec les raisons notées (qualitatif, pas statistique) | avant la bascule du domaine |
| Reproductibilité : entrées avec modèle daté, date, empreinte des prompts, commit, versions des jeux | 0 sur 96 | 100 % des nouvelles entrées v2, 96 anciennes marquées paper-v1 | dès le jalon 1 |
| Entretien : services à maintenir | 1 backend + 1 Space + 1 proxy Vercel | 0 serveur (Pages seul) | à la bascule |

Preuves d'usage acceptées faute de mesure : demandes d'évaluation reçues
(bouton de contact, issues GitHub), citations du site, retours des praticiens
interviewés.

## Décisions déjà prises avec l'équipe

- Site statique sur GitHub Pages ; retrait du dépôt public de résultats.
- Protocole v2 pour tout : bogues du wrapper corrigés, modèles d'API existants
  réévalués ; les anciennes entrées gardées en archive, marquées paper-v1.
- Modèles à raisonnement : deux entrées séparées (sans et avec).
- Demande d'évaluation : bouton de contact (aucune adresse affichée) et gabarit
  d'issue GitHub.
- Unité « % » dans l'en-tête des colonnes, nombres seuls dans les cellules.
- Archiver l'état du dépôt (étiquette Git) avant de retirer la soumission.
- Aucune mesure d'audience sur le site (vie privée maximale) ; risque assumé :
  l'hypothèse « des praticiens viennent » ne se vérifie que par entrevues et
  par les demandes reçues.
- Réévaluation en v2 de tous les modèles d'API sans test préalable v1/v2 ;
  risque assumé : le site et l'article peuvent diverger. Mitigation : note de
  protocole publique, anciennes entrées gardées en archive, écart v1/v2 mesuré
  après coup sur les modèles évalués dans les deux protocoles.
- Fournisseurs : aucun délai garanti ; une seule évaluation par identifiant de
  modèle daté (pas de réessai pour améliorer un score).

## Lean UX Canvas

1. Problème d'affaires : COLE a de l'autorité scientifique mais n'est ni lisible
   ni à jour, donc peu utilisé hors de la recherche.
2. Résultats d'affaires : citations et usage du classement, délai de mise à
   jour, coût d'entretien nul.
3. Utilisateurs : les trois publics ci-dessus.
4. Résultats pour l'utilisateur : choisir ou comprendre en quelques minutes,
   avec une preuve consultable.
5. Solutions envisagées : A) site statique Pages avec données JSON versionnées
   (retenue) ; B) garder le backend, retirer seulement le formulaire ;
   C) carnet interactif publié (type notebook) ; D) tableau de bord hébergé tiers.
6. Hypothèses : voir ci-dessous.
7. À apprendre d'abord : le niveau intermédiaire (radar par catégorie) suffit-il
   à un praticien pour choisir ?
8. Plus petit travail : une page « Choisir un modèle » avec un radar par
   catégorie sur 6 modèles, testée avec 5 praticiens.

## Hypothèses classées par risque

| Hypothèse | Si fausse | Confiance | Coût pour vérifier |
|---|---|---|---|
| Les 23 tâches se regroupent en catégories compréhensibles et le radar par catégorie reflète bien la qualité d'un modèle | La page de niveau 2 trompe les praticiens | moyenne | faible : calcul sur les données existantes plus 5 entrevues |
| Les résultats v2 sont assez proches de v1 pour garder une continuité avec l'article | L'article et le site se contredisent | faible | moyen : réévaluer 3 modèles d'API en v1 et en v2 |
| Des praticiens consultent un classement académique pour choisir un modèle | Le public 1 est inventé ; on sert surtout des chercheurs | moyenne | faible : entrevues, statistiques de visite |
| Les jeux de test publics sont identiques aux privés (ordre et contenu) | Le pipeline note mal, ou fuit des étiquettes | moyenne | faible : comparer les empreintes |
| Un site sans dépôt n'éloigne pas les fournisseurs | Moins de visibilité | moyenne | faible |

## Non-objectifs

- Pas de dépôt de résultats ni de comptes : personne ne peut ajouter une entrée
  sans passer par l'équipe, parce que la vérification manuelle ne tient pas à
  l'échelle et que les étiquettes doivent rester privées.
- Pas de données par exemple publiées : cela divulguerait les étiquettes des
  jeux de test.
- Pas de courriel affiché en clair sur le site : bouton de contact seulement.
- Pas de mode sombre dans la première version : décision de design à part, pour
  tenir le délai.
- Pas de rang unique « meilleur modèle » sans contexte : le classement général
  reste comme vue de référence, mais la page praticien compare par catégorie.
- Pas de nouveaux jeux de tâches dans ce chantier : les 23 tâches restent.
- Pas d'évaluation à la demande avec délai garanti, ni payante, ni de
  résultats privés avant publication (embargo) pour les fournisseurs.
- Pas d'API publique des résultats au-delà du fichier JSON versionné.

## Critères d'acceptation minimaux

- Langues : EN et FR, parité des textes ; la page de vulgarisation existe dans
  les deux.
- Accessibilité : le radar a une alternative tableau lisible au clavier et par
  lecteur d'écran ; contrastes AA mesurés ; focus visible.
- Étiquettes privées : aucun fichier publié ne contient de résultat par exemple
  ni d'étiquette ; une vérification automatique le contrôle avant chaque
  publication. Les entrées de test publiques (`graalul/COLE-public`) doivent
  avoir les mêmes empreintes que les entrées privées (à vérifier).
- Cas limites : modèle sans coût public (champ nul affiché « n.d. »), modèle à
  raisonnement (deux entrées liées), entrée paper-v1 (badge de protocole),
  tâche non évaluée (NA expliqué, jamais un zéro).
- Chiffres : une décimale dans le tableau du site ; l'article rapporte deux
  décimales (règle de recherche) ; la page de niveau avancé donne deux
  décimales.
- Aucune adresse courriel affichée ; contact par bouton.

## Économie et condition d'arrêt

- Les clés sont celles de licences académiques sans plafond ; le suivi de coût
  (jetons, coût estimé, latence) est tout de même journalisé par appel pour
  chaque modèle (champ `billed: false` pour les licences académiques).
- Condition d'arrêt de la réévaluation de masse : si l'écart v1/v2 mesuré sur
  les premiers modèles dépasse 1 point en moyenne ou déplace des rangs du top
  10, on s'arrête et on tranche (étape ajoutée même si le test préalable est
  refusé).
- Condition d'arrêt du projet : le test de niveau 2 échoue (moins de 3
  praticiens sur 5) : on abandonne la page radar et on reprend l'alternative B
  ou C ci-dessous.

## Découpe : tranche 1 puis suite

1. Tranche 1 (livrable seule, de bout en bout) : maquette statique « Choisir un
   modèle » avec un radar par catégorie sur 6 modèles (données actuelles),
   testée avec 5 praticiens nommés avant d'engager la migration Pages et les
   trois niveaux. Les 5 praticiens sont à nommer par l'équipe (organisation,
   rôle, décision de modèle récente) : point ouvert.
2. Si le test réussit : registre de modèles et pipeline d'évaluation v2
   (jalon 1 : un modèle sur 3 tâches), puis migration vers GitHub Pages avec
   archivage (étiquette Git), puis niveaux 1 et 3, puis refonte visuelle
   complète.
3. Si le test échoue : retour au cadrage (alternatives B à D).

## Réévaluation de la solution ancrée

Elle répond au problème pour la fraîcheur, l'entretien et la reproductibilité.
Elle ne répond pas seule à la lisibilité : c'est la page à trois niveaux et la
refonte visuelle qui la portent, et l'hypothèse la plus risquée (le radar
suffit) doit être testée avant de bâtir les trois niveaux en entier.
