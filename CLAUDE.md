# COLE — Quebec French NLU Benchmark

## Project overview
COLE is a multidisciplinary Quebec French Natural Language Understanding benchmark with 23 tasks.
- **Backend**: FastAPI (port 8000) — submission API, HuggingFace dataset evaluation
- **Frontend**: Next.js 16 (port 8001) — leaderboard, submission form, bilingual (EN/FR)
- **Deployment**: Docker container on HuggingFace Spaces (nginx on port 7860 proxies both)

## Quick start
```bash
# Backend
export HF_TOKEN=hf_...
pip install -r cole/requirements.txt
uvicorn cole.backend.submission_api:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend && npm ci && npm run dev

# Tests (requires HF_TOKEN for dataset access)
pip install -r tests/tests_requirements.txt
pytest
```

## Key directories
- `cole/backend/` — FastAPI app (`submission_api.py` is the entry point)
- `cole/dataset/` — HuggingFace dataset loading (repo: `graalul/COLE`)
- `cole/task/` — Task definitions and evaluation logic
- `cole/metrics/` — Metric wrappers (accuracy, F1, pearson, fquad); `mixed_questions.py` evaluates JSONL files mixing several question types (Netquiz/COLE corpus)
- `frontend/src/app/` — Next.js App Router pages and components
- `tests/` — pytest tests (skip automatically without HF_TOKEN)

## Commands
```bash
make lint        # Run pylint + eslint
make format      # Check black formatting
make test        # Run pytest
make build       # Build frontend
make docker      # Build Docker image
make all         # lint + format + test + build
```

## CI/CD
- **Formatting**: `black --check .` (Python 3.12)
- **Linting**: `pylint cole/ tests/` (Python 3.10, 3.11, 3.12)
- **Tests**: `pytest` (Python 3.12, requires HF_TOKEN secret)
- **Frontend build**: `npm ci && npm run lint && npm run build`
- **Docker build**: builds and validates the Docker image
- **Deploy**: pushes to HuggingFace Spaces on main/dev push

## Evaluating mixed-type question files
The Netquiz/COLE corpus stores several question types in a single JSONL file, each
row keeping its type in a `question_type` field. `cole.metrics.mixed_questions`
picks the metric per row (reusing the `fquad_metric` primitives) and reports a
per-type score plus two composites (unweighted, GLUE-style; and weighted by the
instance count per type):
```bash
python -m cole.metrics.mixed_questions gold.jsonl
python -m cole.metrics.mixed_questions gold.jsonl --predictions preds.jsonl --output report.json
```
Supported types and their metric: `single_choice`/`true_false` (accuracy),
`multiple_choice` (set F1), `short_answer` (FQuAD EM+F1), `association` (pair F1),
`categorization` (per-element accuracy), `ordering` (exact match + pairwise concordance).

## Conventions
- Python: black formatting (line-length 88), pylint score must be 10.0
- Frontend: ESLint with eslint-config-next flat config
- All components use `'use client'` directive (client-side i18n)
- Translations in `frontend/src/app/{en,fr}/translation.json`
