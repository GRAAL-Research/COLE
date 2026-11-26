# COLE static site

Source of truth for the COLE results site: seven bilingual (EN/FR) static pages, plain
JavaScript, no framework and no build step to serve them. The generated HTML is committed.
The text shown on the pages stays in French and English; everything else is in English.

## Layout

- `*.html`: generated pages (`index`, `model`, `choose-a-model`, `all-results`, `explore`,
  `plain-language`, `level-3`). Do not edit by hand, edit `build_pages.py`.
- `app.js`, `data.js`, `model.js`, `choose.js`, `results.js`, `explore.js`, `tokens.css`: client code and styles.
- `data/`: `models.json`, `extra.json`, `leaderboard-snapshot.json` (generated), `categories.json`,
  `article.json` (hand-written), `inputs/` (see its README).
- `assets/` (archival pictures and `credits.json`), `fonts/`, `cards/` (share cards).
- `build_pages.py`, `build_models.py`, `build_extra.py`, `build_cards.py`, `refresh_data.py`, `check_links.py`.

## Build

From the repo root, with Python 3.10 or later and no third-party package:

```bash
python3 site/build_pages.py   # rewrites the seven HTML pages, then runs the link check
python3 site/check_links.py   # link check alone: local targets and anchors, exit 1 on failure
```

`build_cards.py` regenerates the share cards in `cards/`. It needs Playwright (Chromium) to
render the PNG and is run by hand only.

## Serve locally

```bash
python3 -m http.server --directory site 8000
```

Then open http://localhost:8000/.

## Data refresh

```bash
python3 site/refresh_data.py                         # every entry of the repo leaderboard
python3 site/refresh_data.py --keep-snapshot-models  # only models already in the committed snapshot
python3 site/build_pages.py
```

Pipeline, all from files of this repository:

1. `cole/backend/results/leaderboard.json` is reshaped into `data/leaderboard-snapshot.json`
   (the live API format; emails are never copied). The published snapshot was taken from the
   live API: for its 96 models the scores are identical to the repo file, so the published
   `models.json` and `extra.json` are reproduced byte for byte with `--keep-snapshot-models`.
2. `build_models.py` computes `data/models.json`: task scores, category means (mean of the
   tasks a model has, never zero-filled), overall score, rank, family, size.
3. `build_extra.py` computes `data/extra.json`: chance references from the random baseline.

The script stops with a clear message when an input file is missing.

Without `--keep-snapshot-models`, the repo file holds more entries than the published
snapshot (five Cohere models at the time of writing). Some page texts say "96", so check
them before publishing a larger snapshot. `SNAPSHOT_DATE` in `build_models.py` is set by hand.

What cannot be reproduced from the repository:

- The original live-API snapshot itself (submission ids, the 96-entry selection): the repo
  file replaces it. Submission ids of new entries are synthetic (`repo:<model name>`).
- Model sizes for seven models, matched by hand from `predictions/llm_details.csv`
  (`data/inputs/size_from_details.json`, provenance in `data/inputs/README.md`).
- The quiz items and the Quebec task list in `build_extra.py`, and `data/categories.json`,
  `data/article.json`: hand-written editorial content.

## APPLY_UNRELIABLE_TASKS

`APPLY_UNRELIABLE_TASKS` in `build_models.py` (default `False`). The free-text tasks fquad,
piaf and wsd show exact zeros for ten API models, which looks like an evaluation failure
(raw predictions unavailable), and they are under verification. With `True`, those task
scores become n.d. (absent, left out of the means, never zero) for API entries whose fquad
is exactly 0 on both f1 and exact_match. Rebuild data and pages after changing it.

## Deployment

Today, the Vercel project `colebenchmark-proxy` serves a copy of this folder from its
`public/` directory, and proxies the legacy routes to the Hugging Face Space. Updating the
site means copying the built folder into that `public/` directory. Planned: move to GitHub
Pages, serving `site/` directly from this repository.

## Tests

```bash
pytest tests/site --no-cov
```

Unit tests of the data logic (category means, ranking, n.d. handling under the flag) and a
check that the committed `models.json` matches the committed snapshot. No network.
