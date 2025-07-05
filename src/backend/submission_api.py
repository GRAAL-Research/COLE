import glob
import json
import logging
import sys
import uuid
from pathlib import Path
from typing import Dict, List, Any

from fastapi import FastAPI, UploadFile, Form, File
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from src.backend.evaluation import compute_tasks_ratings
from src.backend.submit_tools import unzip_predictions_from_zip
from src.backend.validation_tools import (
    validate_submission_tasks_name,
    validate_submission_json,
    validate_submission_template,
)
from src.task.task import Task
from src.task.task_factory import (
    tasks_factory,
)

# --- Paths configuration ---
BASE_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = BASE_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

RESULTS_DIR = BASE_DIR / "src" / "backend" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI()
app.mount("/results", StaticFiles(directory=str(RESULTS_DIR)), name="results")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/submit")
async def submit(
    email: str = Form(...),
    predictions_zip: UploadFile = File(...),
    display_name: str = Form(...),
):
    logging.info(f"Submission from {email!r} as {display_name!r}.")

    zip_bytes = await predictions_zip.read()
    submission_json = unzip_predictions_from_zip(zip_bytes)

    validate_submission_template(submission_json)

    validate_submission_tasks_name(submission_json)
    validate_submission_json(submission_json)

    tasks: List[Task] = tasks_factory(submission_json)

    submission_response = compute_tasks_ratings(tasks=tasks, submission=submission_json)
    submission_response.update(
        {
            "display_name": display_name,
        }
    )

    out_path = RESULTS_DIR / f"{uuid.uuid4()}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(submission_response, f, ensure_ascii=False, indent=2)

    return JSONResponse(content=submission_response)


@app.get("/leaderboard")
async def leaderboard() -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    for accepted_submission in glob.glob(str(RESULTS_DIR / "*.json")):
        with open(accepted_submission, encoding="utf-8") as f:
            data = json.load(f)

        # TODO

    return entries


@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running."}
