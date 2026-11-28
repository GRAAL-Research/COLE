# Relance de fquad, piaf et wsd pour les modèles API

Procédure à suivre sur le serveur. Aucune commande de ce document n'a été exécutée par
l'auteur : tout appel d'API est payant et doit être lancé par David.

## 1. Objectif et raison

Dans `cole/backend/results/leaderboard.json` (101 entrées), onze modèles API ont un score fquad
(f1) de exactement 0.0 : voir la section 4. Pour un modèle fort, un f1 de 0.0 sur une tâche
extractive est presque certainement une panne du pipeline d'évaluation, pas une mesure.

Les correctifs sont dans la branche `fix/api-wrapper-extraction-bugs` :

- Une relance réussie après une exception renvoyait None (donc NA, puis un score de 0) : corrigé.
- Les réponses génératives (fquad, piaf, wsd) étaient coupées au dernier « : » et tous les espaces
  étaient supprimés, ou remplacées par un chiffre trouvé dans le texte : le post-traitement de
  label est maintenant réservé aux tâches de classification.
- Les paramètres `tools` et `tool_choice` d'une tâche de classification restaient actifs sur les
  tâches génératives suivantes : ils sont maintenant remis à zéro avant chaque tâche générative.
- Pour les modèles Claude, une réponse générative (bloc texte) provoquait une exception : corrigé.
- Les métriques fquad, piaf et wsd excluent maintenant les prédictions en échec (None, vide, « NA »,
  « -1 »), les comptent dans `na_count`, et lèvent une erreur si plus de 20 % des prédictions
  sont en échec. Un échec de pipeline ne peut plus apparaître comme un score de 0.0.
- Nouvelle option `--tasks` pour ne relancer que certaines tâches.

## 2. Prérequis

Vérifié dans le code :

- Python 3.12 (CI) avec les dépendances : `pip install -r cole/requirements.txt`.
- Déployer la branche `fix/api-wrapper-extraction-bugs` (ou le commit fusionné qui la contient) et
  lancer les commandes depuis la racine du dépôt.
- Le fichier `.env` à la racine est chargé par le pipeline (`load_dotenv(".env")`) ; le script
  ci-dessous le relie automatiquement dans le dossier de sortie.
- `HF_TOKEN` : requis pour charger le jeu de données privé `graalul/COLE` (split `test`).
- Variables d'environnement des clés API (noms uniquement ; lues dans
  `cole/language_model/private_language_model_factory.py`) :

| Fournisseur | Variable |
|---|---|
| OpenAI (o3, o1, gpt-4.1, gpt-4o) | `openai_api_key` |
| Anthropic (Claude) | `anthropic_token` |
| Mistral | `mistral_token` |
| xAI (Grok) | `XAI_API_KEY` |
| OpenRouter (gemini-2.5-flash) | `open_route_api_key` |
| Cohere | `cohere_api_key` |

- WandB : le pipeline appelle `wandb.init(project=<COLE-final>, entity="doctorate")` (valeurs
  codées en dur). Il faut donc un `WANDB_API_KEY` valide pour l'entité `doctorate`, ou
  `WANDB_MODE=offline` pour ne rien publier (variable standard de WandB ; non testée ici). Pour le
  smoke test, utiliser `WANDB_MODE=offline` afin de ne pas créer de runs parasites dans le projet.

## 3. Option `--tasks` (vérifiée par un test unitaire)

`--tasks fquad,piaf,wsd` restreint le groupe choisi par `--tasks_group` aux tâches nommées. Un nom
inconnu pour le groupe lève une erreur avant tout appel d'API. Sans l'option, tout le groupe est
exécuté comme avant. Test : `tests/evaluation/test_select_tasks.py`.

Correction d'un constat antérieur : le pipeline exige `--tasks_group` (sinon `ValueError`), accepte
`--models_name` comme nom de fournisseur (clé de `private_llm`) ou liste de modèles séparés par des
virgules, et écrit ses résultats dans `./results` relatif au dossier courant.

## 4. Modèles et identifiants

> **Retirés le 28 novembre 2026 :** `claude-opus-4-20250514` et `claude-sonnet-4-20250514` ne sont plus servis par l'API Anthropic (réponse 404 `not_found_error`, vérifiée par un appel direct). Leur relance est impossible ; leurs anciens scores à 0 sur fquad/piaf/wsd ne peuvent plus être refaits.

Sélection : modèles de `cole/backend/results/leaderboard.json` qui appartiennent à
`predictions/all_llms.py` (`private_llm`) et dont le f1 fquad vaut exactement 0.0 (constaté dans le
fichier). Ce sont onze modèles, pas dix ; `command-r7b-12-2024` est le moins « fort » des onze et
peut être retiré si David veut s'en tenir à dix.

| Identifiant à passer au CLI | Fournisseur | fquad f1 | piaf f1 | wsd em |
|---|---|---|---|---|
| `pixtral-large-latest` | mistral | 0.0 | 0.0 | 0.0 |
| `mistral-large-latest` | mistral | 0.0 | 0.0 | 0.0 |
| `o3-2025-04-16` | openai | 0.0 | 0.0 | 0.0 |
| `o1-2024-12-17` | openai | 0.0 | 0.0 | 0.0 |
| `gpt-4.1-2025-04-14` | openai | 0.0 | 0.0 | 1.2 |
| `gpt-4o-2024-08-06` | openai | 0.0 | 0.0 | 0.0 |
| `grok-3-latest` | xai | 0.0 | 0.0 | 0.0 |
| `grok-3-fast-latest` | xai | 0.0 | 0.0 | 0.0 |
| `google/gemini-2.5-flash` | openrouter | 0.0 | 0.0 | 0.0 |
| `command-r7b-12-2024` | cohere | 0.0 | 0.0 | 0.0 |

Autres entrées suspectes (non incluses par défaut) : quatre modèles ont un f1 de 10.4167 à la fois
sur fquad et sur piaf (`claude-sonnet-4-20250514`, `gpt-5-2025-08-07`, `grok-4-0709`,
`grok-4-fast-non-reasoning`) et trois ont 2.78 sur fquad et 10.42 sur piaf (`grok-3-mini-latest`,
`grok-3-mini-fast-latest`, `google/gemini-2.5-pro`). Ces valeurs répétées ressemblent à un artefact
du même type ; à relancer dans un second temps après validation du premier lot. Non vérifié : la
cause exacte.

## 5. Smoke test obligatoire (un modèle par fournisseur, 20 exemples)

Lancer avant tout run complet, avec une sortie séparée et sans publier sur WandB :

```bash
export WANDB_MODE=offline
RUN_DIR=runs/smoke MAX_EXAMPLES=20 scripts/relance_fquad_piaf_wsd.sh \
  gpt-4o-2024-08-06 claude-opus-4-20250514 mistral-large-latest \
  grok-3-latest google/gemini-2.5-flash command-r7b-12-2024
```

À vérifier pour chaque modèle (dans `runs/smoke/logs/<modèle>.log` et
`runs/smoke/results/<modèle>_metrics.json`) :

- Pas de déluge de NA : le log ne contient pas de lignes « Generated a NA when model inference. »
  en quantité, et `Number of None` / `max retries exceeded` (avertissements de `print_none`) sont
  absents ou très faibles.
- f1 fquad nettement supérieur à 0 pour un modèle fort (ordre de grandeur attendu : dizaines de
  points, comme `gpt-4o-mini` à 33.9 ou `deepseek-chat` à 63.5 dans le classement actuel).
- `na_count` : la clé n'apparaît dans les métriques que s'il y a des prédictions en échec ; si elle
  apparaît, elle doit rester sous 20 % de 20 exemples (soit 4). Au-delà, la tâche est écartée des
  métriques et l'erreur est écrite dans le log : le script signale alors le modèle en échec.
- Aucun exemple de réponse tronquée : ouvrir le fichier de prédictions
  (`runs/smoke/results/<modèle>_<date>.json`) et lire quelques réponses fquad, qui doivent
  contenir des phrases ou groupes de mots complets avec espaces.

Si un seul de ces points échoue, arrêter et transmettre le log.

## 6. Run complet

Commande pour un modèle (sans le script) :

```bash
python -m cole.evaluation.evaluation_pipeline_private_llm \
  --models_name gpt-4o-2024-08-06 --tasks_group cole --tasks fquad,piaf,wsd
```

Script pour les onze modèles, un à la fois, avec un journal par modèle (aucun secret affiché) :

```bash
scripts/relance_fquad_piaf_wsd.sh                 # les onze modèles par défaut
scripts/relance_fquad_piaf_wsd.sh o3-2025-04-16   # ou une liste explicite
```

- Sorties : `runs/relance-fquad-piaf-wsd/logs/<modèle>.log` et
  `runs/relance-fquad-piaf-wsd/results/` (prédictions et métriques).
- Reprise : un modèle dont le fichier de métriques contient déjà fquad, piaf et wsd est ignoré. Pour
  en refaire un, supprimer son fichier `_metrics.json`.
- Le script termine en erreur et liste les modèles dont les métriques sont absentes ou incomplètes
  (par exemple quand la garde de 20 % a écarté une tâche).
- Les noms de fichiers remplacent `/` par `_` (par exemple `google_gemini-2.5-flash_metrics.json`).

## 7. Coûts

Chaque exemple fait un appel d'API, avec jusqu'à 11 tentatives en cas d'erreur (`max_retries` = 10,
pause de 5 secondes). Facteurs de coût :

- nombre d'exemples de fquad, piaf et wsd (split `test` de `graalul/COLE`) ;
- tokens d'entrée (contexte + question) et de sortie (réponse courte, extractive) ;
- tarif par modèle ;
- modèles de raisonnement `o3-2025-04-16` et `o1-2024-12-17` : nettement plus chers par appel (jetons
  de raisonnement facturés en sortie ; le code fixe `reasoning_effort: low` pour ces deux modèles,
  et `max_completion_tokens: 4096` pour o3) ;
- `google/gemini-2.5-flash` via OpenRouter : modèle à raisonnement possible, facturation OpenRouter.

Non estimé : le nombre d'exemples par tâche n'a pas pu être lu (jeu de données privé, `HF_TOKEN`
absent dans l'environnement de travail de l'auteur) et les tarifs actuels n'ont pas été consultés.
Le smoke test à 20 exemples donne une première mesure réelle (tokens facturés par modèle sur le
tableau de bord du fournisseur), à multiplier par le nombre d'exemples du split.

## 8. Critères d'acceptation

- f1 fquad supérieur à 0 pour les modèles forts (`gpt-4o`, `gpt-4.1`, `o3`, `claude-opus-4`,
  `mistral-large`) ; un 0.0 résiduel doit être expliqué par le log, pas accepté.
- Nombre de prédictions NA sous la garde de 20 % pour chacune des trois tâches (clé `na_count`
  rapportée ; absente quand il n'y a aucun échec).
- Les trois tâches (fquad, piaf, wsd) présentes dans le fichier de métriques de chaque modèle.
- piaf et wsd non nuls pour les modèles forts.

## 9. Exporter les scores et remplacer les résultats du classement

Ce qui est vérifié dans le code :

- Le classement servi par `GET /leaderboard` lit des fichiers JSON dans le dossier de résultats du
  backend (`cole/backend/results/leaderboard.json` : liste d'objets `model_name`, `model_url`,
  `tasks` avec, par exemple, `{"fquad": {"f1": ..., "exact_match": ...}}`).
- `predictions/wandb-to-jsonl.py` reconstruit un `leaderboard.json` à partir des runs WandB du projet
  `doctorate/<projet>` (option `--merge_per_model` pour fusionner les runs d'un même modèle).
- Le fichier `_metrics.json` du pipeline a une structure différente
  (`{"tasks": [{"fquad": {"fquad": {"exact_match": ..., "f1": ...}}}]}`).

Non documenté et non vérifié : il n'existe aucun script dans le dépôt qui remplace seulement trois
tâches pour onze modèles dans `leaderboard.json`, et on n'a pas vérifié si `--merge_per_model` fait
prévaloir le run le plus récent. Voie recommandée : ne pas modifier le classement à la main ; envoyer
les fichiers `_metrics.json` (section 10), et le remplacement sera fait par un petit script
dédié, revu, qui ne touche que `fquad`, `piaf` et `wsd` de ces onze modèles.

## 10. Retour d'information pour mettre à jour les maquettes statiques

Transmettre :

1. le dossier `runs/relance-fquad-piaf-wsd/results/` (fichiers `_metrics.json`) ;
2. les journaux `runs/relance-fquad-piaf-wsd/logs/` ;
3. pour chaque modèle : f1 et exact_match de fquad, f1 et exact_match de piaf, exact_match de wsd,
   et `na_count` s'il est présent ;
4. le commit déployé (`git rev-parse HEAD`) et la date du run ;
5. le coût réel par fournisseur lu sur les tableaux de bord, pour mettre à jour l'estimation.

## 11. Vérifié dans le code, non vérifié

Vérifié dans le code et par tests unitaires avec client simulé : relance, extraction générative,
isolation des paramètres, lecture des blocs texte Claude, garde de NA des métriques, sélection
`--tasks`.

Non vérifié : tout appel réel à une API ; la taille réelle de fquad, piaf et wsd ; les tarifs ;
la cause exacte du f1 de 10.4167 ; le comportement de WandB hors ligne ; la fusion dans le
classement ; le script bash n'a été vérifié que par `bash -n` (syntaxe), pas exécuté.
