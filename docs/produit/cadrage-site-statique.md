# Cadrage : COLE, site statique et refonte

Statut : brouillon à valider. Date : 2026-11-26.

## Solution ancrée (mise de côté, réévaluée à la fin)

« Un site statique sur GitHub Pages, sans dépôt de résultats, avec un classement
refait et une page de vulgarisation à trois niveaux. »

## Problème

Une personne qui veut savoir quel modèle de langage est fiable en français
québécois ouvre colebenchmark.org et trouve un tableau de 96 lignes sur 26
colonnes, lisible seulement par un spécialiste. Elle ne voit ni la date
d'évaluation, ni le coût, ni la taille, ni ce que mesure chaque colonne. Les
modèles récents manquent : aucun Claude 5, aucun Cohere de 2026, ni plusieurs
modèles de la liste du dépôt (Claude Sonnet 4.5, GPT-5.1, Gemini 3 Pro).
Les résultats vieillissent donc sans que personne ne le sache, et ceux qui ne
sont pas spécialistes ne comprennent pas ce que COLE mesure.

Pourquoi ce n'est pas résolu : le site est né comme annexe d'un article, avec un
backend FastAPI à entretenir sur HuggingFace, un protocole d'évaluation qui
perd des appels en silence (relance qui devient NA, erreurs confondues, aucun
suivi de coût) et aucun processus pour ajouter un modèle.

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

## Résultat visé (métriques proposées, valeurs actuelles à mesurer)

| Métrique | Aujourd'hui | Cible | Échéance |
|---|---|---|---|
| Fraîcheur : modèles frontière sortis depuis moins de 90 jours et évalués | 0 des 4 Claude 5 ; Claude 4.x seulement | 100 % des modèles frontière listés au registre, délai de moins de 30 jours après la sortie | 3 mois après la mise en ligne |
| Lisibilité : une personne non spécialiste répond correctement à « quel modèle est le meilleur en inférence ? » sans aide | non mesuré | 4 sur 5 en test avec 5 personnes | avant la mise en ligne |
| Entretien : serveurs ou services à entretenir | 1 backend + 1 Space + 1 proxy | 0 (GitHub Pages seul) | à la bascule |
| Reproductibilité : entrées avec date, modèle daté, empreinte des prompts, commit | 0 sur 96 | 100 % des nouvelles entrées | dès le jalon 1 |

## Décisions déjà prises avec l'équipe

- Site statique sur GitHub Pages ; retrait du dépôt public de résultats.
- Protocole v2 pour tout : bogues du wrapper corrigés, modèles d'API existants
  réévalués ; les anciennes entrées gardées en archive, marquées paper-v1.
- Modèles à raisonnement : deux entrées séparées (sans et avec).
- Demande d'évaluation : bouton de contact (aucune adresse affichée) et gabarit
  d'issue GitHub.
- Unité « % » dans l'en-tête des colonnes, nombres seuls dans les cellules.
- Archiver l'état du dépôt (étiquette Git) avant de retirer la soumission.

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
  reste, mais la page praticien compare par catégorie.

## Réévaluation de la solution ancrée

Elle répond au problème pour la fraîcheur, l'entretien et la reproductibilité.
Elle ne répond pas seule à la lisibilité : c'est la page à trois niveaux et la
refonte visuelle qui la portent, et l'hypothèse la plus risquée (le radar
suffit) doit être testée avant de bâtir les trois niveaux en entier.
