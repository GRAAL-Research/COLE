# Contributing to COLE

Thank you for your interest in contributing to the COLE benchmark!

For detailed architecture documentation (backend, frontend, evaluation pipeline, CI/CD), see [docs/architecture.md](docs/architecture.md).

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- A HuggingFace token with access to `graalul/COLE`

### Backend

```bash
pip install -r cole/requirements.txt
export HF_TOKEN=your_token
uvicorn cole.backend.submission_api:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Docker

```bash
docker build -t cole .
docker run -p 7860:7860 -e HF_TOKEN=your_token cole
```

## Submitting Model Results

1. Load test data from `graalul/COLE-public` on HuggingFace
2. Format predictions as JSON:

```json
{
  "model_name": "your_model_name",
  "model_url": "https://huggingface.co/your_model",
  "tasks": [
    { "allocine": { "predictions": [1, 0, 1, ...] } },
    { "xnli": { "predictions": [0, 2, 1, ...] } }
  ]
}
```

3. Compress into a ZIP archive (max 50MB)
4. Submit at [colebenchmark.org](https://colebenchmark.org/)

## Code Quality

```bash
make all                 # Run all checks (format, lint, test, build)

# Or individually:
make format              # Check formatting (black)
make lint                # Linting (pylint + eslint)
make test                # Tests (requires HF_TOKEN for full suite)
make build               # Build frontend
```

## Questions?

Open an issue or email david.beauchemin@ift.ulaval.ca.
