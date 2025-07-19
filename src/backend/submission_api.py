import glob
import json
import logging
import sys
import uuid
from contextlib import asynccontextmanager
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Any

from fastapi import FastAPI, UploadFile, Form, File
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from src.backend.evaluation import compute_tasks_ratings
from src.backend.submit_tools import unzip_predictions_from_zip
from src.dataset.datasets import preload_all_datasets
from src.backend.validation_tools import (
    validate_submission_tasks_name,
    validate_submission_json,
    validate_submission_template,
)
from src.task.task import Task
from src.task.task_factory import (
    tasks_factory,
)


BASE_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = BASE_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

RESULTS_DIR = BASE_DIR / "src" / "backend" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
FRONTEND_DIR = BASE_DIR / "frontend"


@asynccontextmanager
async def lifespan(application: FastAPI = None):  # pylint: disable=unused-argument
    # Load the ML model
    preload_all_datasets()
    yield


app = FastAPI(lifespan=lifespan)
app.mount("/results", StaticFiles(directory=str(RESULTS_DIR)), name="results")
front_end_info_message = f"The Front-end directory is: {FRONTEND_DIR}"
logging.info(front_end_info_message)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/submit")
async def submit(
    email: str = Form(...),
    predictions_zip: UploadFile = File(...),
    display_name: str = Form(...),
):
    info_message = f"Submission from {email!r} as {display_name!r}."
    logging.info(info_message)
    zip_bytes = await predictions_zip.read()
    submission_json = unzip_predictions_from_zip(zip_bytes)

    validate_submission_template(submission_json)
    validate_submission_tasks_name(submission_json)
    validate_submission_json(submission_json)

    tasks: List[Task] = tasks_factory(submission_json)
    submission_response = compute_tasks_ratings(tasks=tasks, submission=submission_json)

    submission_id = str(uuid.uuid4())
    submission_response.update(
        {
            "display_name": display_name,
            "email": email,
            "submission_id": submission_id,
        }
    )

    out_path = RESULTS_DIR / f"{submission_id}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(submission_response, f, ensure_ascii=False, indent=2)

    get_leaderboard_entries.cache_clear()

    return JSONResponse(content=submission_response)


@lru_cache(maxsize=1)
def get_leaderboard_entries() -> List[Dict[str, Any]]:

    entries: List[Dict[str, Any]] = []

    for filepath in glob.glob(str(RESULTS_DIR / "*.json")):
        try:
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)

            if "model_name" not in data or "tasks" not in data:
                continue

            results = {}
            for task_obj in data["tasks"]:
                for task_name, values in task_obj.items():
                    results[task_name] = values

            if not results:
                continue

            entry = {
                "submission_id": data.get("submission_id") or str(uuid.uuid4()),
                "display_name": data.get("display_name")
                or data.get("model_name")
                or "Unnamed Model",
                "email": data.get("email", "N/A"),
                "results": results,
            }

            entries.append(entry)

        except Exception as e:
            error_message = f"Error processing file {filepath}: {e}"
            logging.error(error_message)
            continue

    return entries


@app.get("/leaderboard")
async def leaderboard() -> List[Dict[str, Any]]:

    return get_leaderboard_entries()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running."}


@app.get("/")
async def home():
    return {"status": "working"}
