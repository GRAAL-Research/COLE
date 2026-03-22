# Contributing to COLE

Thank you for your interest in contributing to the COLE benchmark!

## Local Development Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- A HuggingFace account with access to the `graalul/COLE` dataset

### Backend

```bash
pip install -r src/requirements.txt
uvicorn src.backend.submission_api:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend runs on port 3000 by default and proxies API calls to the backend on port 8000.

### Running with Docker

```bash
docker build -t cole .
docker run -p 7860:7860 -e HF_TOKEN=your_token cole
```

## Submitting Model Results

1. Run inference on the COLE test splits (available via `graalul/COLE-public` on HuggingFace)
2. Format predictions as a JSON file:

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

3. Compress the JSON file into a ZIP archive
4. Submit via the website at [colebenchmark.org](https://colebenchmark.org/)

## Code Quality

We use the following tools (install via `pip install -r styling_requirements.txt`):

- **Black** for formatting: `black --check .`
- **PyLint** for linting: `pylint src/ tests/`

## Running Tests

```bash
pip install -r tests/tests_requirements.txt
export HF_TOKEN=your_token  # Required for private dataset access
pytest
```

## Project Structure

```
COLE/
├── frontend/          # Next.js frontend (leaderboard, submission UI)
├── src/
│   ├── backend/       # FastAPI backend (submission API, evaluation)
│   ├── dataset/       # Dataset loading and configuration
│   ├── task/          # Task definitions and metrics
│   └── language_model/ # Model wrappers for inference
├── tests/             # Test suite
├── predictions/       # Prediction processing scripts
├── Dockerfile         # Production container
├── nginx.conf         # Reverse proxy config
└── start.sh           # Container startup script
```

## Questions?

Open an issue or email david.beauchemin@ift.ulaval.ca.
