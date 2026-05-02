# COLE Architecture

## System Overview

COLE runs as a single Docker container with three services behind an nginx reverse proxy, deployed on HuggingFace Spaces.

```mermaid
graph LR
    User([User]) -->|:7860| Nginx
    subgraph Docker Container
        Nginx -->|/api/*| FastAPI[FastAPI :8000]
        Nginx -->|/*| NextJS[Next.js :8001]
        FastAPI -->|reads| HF[(HuggingFace\ngraalul/COLE)]
        FastAPI -->|writes| Results[(results/*.json)]
    end
```

## Backend (FastAPI)

### API Endpoints

```mermaid
graph TD
    subgraph API
        POST[POST /submit] -->|ZIP upload| Validate[Validate format]
        Validate -->|OK| Evaluate[Evaluate predictions]
        Evaluate -->|Save| JSON[results/uuid.json]
        GET_LB[GET /leaderboard] -->|Read all| JSON
        GET_H[GET /health] -->|200| OK[status: healthy]
    end
```

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/submit` | POST | Upload predictions ZIP, evaluate, save results |
| `/leaderboard` | GET | Return all submissions with metrics |
| `/health` | GET | Health check |

### Security

- **Rate limiting**: 5 submissions/minute per IP (slowapi)
- **ZIP validation**: Max 50MB compressed, 200MB decompressed
- **Input validation**: Email (max 320 chars, must contain @), display name (max 200 chars)
- **CORS**: Open origins (proxied through nginx)

### Key Modules

```mermaid
graph TD
    API[submission_api.py] --> VT[validation_tools.py]
    API --> ST[submit_tools.py]
    API --> EV[evaluation.py]
    VT --> TN[task_names.py]
    EV --> TF[task_factory.py]
    TF --> T[task.py]
    T --> MF[metric_factory.py]
    T --> DS[dataset.py]
    MF --> MW[metrics_wrapper.py]
    MF --> FQ[fquad_metric.py]
    DS --> HF[(HuggingFace)]
```

## Frontend (Next.js)

### Pages

```mermaid
graph LR
    subgraph Pages
        Home[/ Home]
        Guide[/guide]
        FAQ[/FAQ]
        Contact[/contact]
        Papers[/papers]
        Benchmarks[/benchmarks]
        Leaderboard[/leaderboard]
        Results[/results/id]
    end
    subgraph Features
        i18n[EN/FR i18n]
        Responsive[Mobile responsive]
        Pagination[Leaderboard pagination]
        Submit[ZIP submission modal]
    end
```

| Page | Description |
|------|-------------|
| `/` | What is COLE, links to paper and GLUE/SuperGLUE |
| `/guide` | How to train, test, and format submissions |
| `/FAQ` | 6 questions with code formatting support |
| `/benchmarks` | 23 tasks organized by 9 NLU categories |
| `/leaderboard` | Sortable table, 25/page, loading skeleton, error states |
| `/papers` | Embedded arxiv PDF viewer |
| `/results/[id]` | Per-submission detailed results |
| `/contact` | Email contact |

### i18n

Full English and French translations in `frontend/src/app/en/translation.json` and `fr/translation.json`. Language switcher in the header persists selection to localStorage.

## Evaluation Pipeline

### Task Flow

```mermaid
graph TD
    Submit[User submits ZIP] --> Unzip[Extract predictions.json]
    Unzip --> Validate[Validate task names & format]
    Validate --> Factory[task_factory creates Task objects]
    Factory --> Compute[Task.compute per task]
    Compute --> Dataset[Load ground truths from HF]
    Compute --> Metric[metric_factory selects metric]
    Metric --> Score[Compute score]
    Score --> Save[Save results JSON]
```

### Tasks (23 total)

Grouped by capability:

| Category | Tasks |
|----------|-------|
| Sentiment | allocine, mms |
| NLI | daccord, fracas, gqnli, lingnli, mnli-nineeleven-fr-mt, rte3-french, sickfr, xnli |
| QA | fquad, french_boolq, piaf |
| Paraphrase | paws_x, qfrblimp |
| Grammar | multiblimp, qfrcola |
| Similarity | sts22 |
| WSD | wsd |
| Quebec French | qfrcore, qfrcort |
| Coreference | wino_x_lm, wino_x_mt |

### Metrics

| Metric | Implementation | Used by |
|--------|---------------|---------|
| Accuracy | HuggingFace `evaluate` | Most classification tasks |
| Pearson | HuggingFace `evaluate` | sickfr, sts22 |
| FQuAD | Custom (F1 + Exact Match) | fquad, piaf |
| ExactMatch | Custom string comparison | wsd |
| F1 | HuggingFace `evaluate` | Classification variants |

## CI/CD Pipeline

```mermaid
graph TD
    Push[git push to main] --> F[Formatting\nblack --check]
    Push --> L[Linting\npylint src/ tests/]
    Push --> T[Tests\npytest]
    Push --> FB[Frontend Build\nnpm ci + lint + build]
    Push --> DB[Docker Build]
    Push --> HF[HF Sync\nDeploy to Space]

    F -->|Python 3.12| Pass
    L -->|Python 3.10-3.12| Pass
    T -->|Python 3.12\nHF_TOKEN required| Pass
    FB -->|Node 20| Pass
    DB -->|cole image| Pass
    HF -->|Orphan branch\nLFS for .jsonl/.pdf| Space[davebulaval/cole]
```

## Deployment

The HF Space deployment uses an orphan branch strategy to handle large `.jsonl` files in git history:

1. Checkout main with LFS
2. Create fresh orphan branch
3. Track `.jsonl` and `.pdf` with Git LFS
4. Remove CI/test files not needed in production
5. Force push to `davebulaval/cole` Space

The Space builds the Docker image and runs the container with nginx on port 7860.
