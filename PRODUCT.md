# COLE : fiche produit

Mise à jour : 2026-11-26. Détail : docs/produit/cadrage-site-statique.md.

## Problème
Le classement COLE est illisible pour les non-spécialistes, vieillit sans date
ni coût, et dépend d'un backend et d'un protocole d'évaluation à entretenir.

## Utilisateurs
Praticiens qui choisissent un modèle ; grand public, médias, étudiants ;
fournisseurs de modèles. Les chercheurs restent servis par le niveau avancé.

## Job to be done
Quand je dois choisir ou comprendre un LLM en français québécois, je veux une
comparaison lisible et datée, afin de décider ou d'expliquer sans me tromper.

## Résultat visé (détail, valeurs actuelles et échéances : docs/produit/cadrage-site-statique.md)
- Couverture : 100 % des modèles du registre évalués en v2 (aujourd'hui 0 sur 19
  absents de `all_llms.py`, plus Claude 5 et Cohere 2026), 3 mois.
- Fraîcheur : moins de 30 jours entre la sortie d'un modèle et son entrée.
- Décision : 4 praticiens nommés sur 5 choisissent entre 2 candidats en moins
  de 3 minutes avec la page niveau 2 (qualitatif), avant la bascule du domaine.
- Reproductibilité : 100 % des nouvelles entrées v2 (aujourd'hui 0 sur 96).
- Entretien : 0 serveur (aujourd'hui backend + Space + proxy).
- Pas de mesure d'audience (décision) : l'usage se juge sur les demandes
  reçues, les citations et les entrevues.

## Non-objectifs
Pas de dépôt public de résultats ; pas de données par exemple ; pas de courriel
affiché ; pas de mode sombre en v1 ; pas de rang unique sans contexte ; pas de
nouveaux jeux de tâches ; pour les fournisseurs : aucun délai garanti, une seule
évaluation par identifiant de modèle daté, ni payant ni embargo.

## Hypothèses à risque
Le radar par catégorie suffit au praticien ; v2 reste proche de v1 ; les
praticiens consultent un classement académique.
