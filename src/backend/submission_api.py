import glob
import json
import logging
import os
import sys
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Any, Union

import huggingface_hub
from fastapi import FastAPI, UploadFile, Form, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request

MAX_ZIP_SIZE_MB = 50

from src.backend.evaluation import compute_tasks_ratings
from src.backend.submit_tools import unzip_predictions_from_zip
from src.dataset.datasets_data import preload_all_datasets
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
    """Called before the backend comes online, is used to load datasets in memory."""
    # Load the ML model
    try:
        token = os.environ.get("HF_TOKEN")
        huggingface_hub.login(token=token)
        preload_all_datasets()
    except Exception as e:
        error_message = f"The datasets could not be loaded : {e}"
        logging.critical(error_message)

    yield


limiter = Limiter(key_func=get_remote_address)
app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    lambda req, exc: JSONResponse(
        status_code=429,
        content={"detail": "Too many submissions. Please try again later."},
    ),
)
app.mount("/results", StaticFiles(directory=str(RESULTS_DIR)), name="results")
front_end_info_message = f"The Front-end directory is: {FRONTEND_DIR}"
logging.info(front_end_info_message)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/submit")
@limiter.limit("5/minute")
async def submit(
    request: Request,
    email: str = Form(...),
    predictions_zip: UploadFile = File(...),
    display_name: str = Form(...),
):
    """Route for making submissions with user generated results.
    :param request : The incoming request (used for rate limiting)
    :param email : The email of the user's submission
    :param predictions_zip : The zip file of the user's predictions'
    :param display_name : The display name associated with the user's submission'
    """
    logging.info("Starting submission")
    if len(display_name) > 200:
        raise HTTPException(
            status_code=400, detail="Display name must be under 200 characters."
        )
    if len(email) > 320 or "@" not in email:
        raise HTTPException(status_code=400, detail="Invalid email address.")
    info_message = f"Submission from {email!r} as {display_name!r}."
    logging.info(info_message)
    zip_bytes = await predictions_zip.read()
    if len(zip_bytes) > MAX_ZIP_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=413, detail=f"ZIP file exceeds {MAX_ZIP_SIZE_MB}MB limit."
        )
    submission_json = unzip_predictions_from_zip(zip_bytes)

    validate_submission_template(submission_json)
    validate_submission_tasks_name(submission_json)
    validate_submission_json(submission_json)

    tasks: List[Task] = tasks_factory(submission_json)
    logging.info("Computation started")
    start = datetime.now()
    submission_response = compute_tasks_ratings(tasks=tasks, submission=submission_json)
    computation_time = datetime.now() - start
    info_message = f"Computation ended in {computation_time}"
    logging.info(info_message)
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
    """Returns all entries currently in the leaderboard.
    Supporte aussi les fichiers JSON qui contiennent une LISTE d'entrées
    et normalise les métriques 'plates' en groupes imbriqués pour le front.
    """

    def _wrap_flat_metrics(task_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Si task_payload est 'plat' (ex: {"accuracy": 94.2}),
        on le transforme en {"<group>": {...}} pour que le front puisse l'agréger.
        Règles de nommage du groupe :
          - présence de exact_match/f1 -> "fquad"
          - sinon présence de acc/accuracy -> "accuracy"
          - sinon présence de pearson/pearsonr/spearman -> "correlation"
          - sinon -> "metrics"
        Les valeurs >1 sont laissées telles quelles (le front normalise déjà % -> [0,1]).
        """
        if not isinstance(task_payload, dict):
            return task_payload

        # si c'est déjà "imbriqué" (une valeur est un dict), on ne touche pas
        if any(isinstance(v, dict) for v in task_payload.values()):
            return task_payload

        keys = set(k.lower() for k in task_payload.keys())
        if {"exact_match", "f1"} & keys:
            group = "fquad"
        elif {"accuracy", "acc"} & keys:
            group = "accuracy"
        elif {"pearson", "pearsonr", "spearman"} & keys:
            group = "correlation"
        else:
            group = "metrics"

        # Rien de spécial pour les warnings ici : le front les considère optionnels
        # et s'attend à "<group>_warning" dans l'objet interne si on veut en fournir.
        return {group: task_payload}

    entries: List[Dict[str, Any]] = []

    for filepath in glob.glob(str(RESULTS_DIR / "*.json")):
        try:
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)

            # Fonction interne qui traite UNE entrée (dict) au bon format minimal
            def process_entry(entry: Dict[str, Any]) -> Union[Dict[str, Any], None]:
                if not isinstance(entry, dict):
                    return None
                if "model_name" not in entry or "tasks" not in entry:
                    return None

                # Re-construire "results" comme le front s'y attend
                results = {}
                for task_obj in entry.get("tasks", []):
                    if not isinstance(task_obj, dict) or len(task_obj) != 1:
                        continue
                    task_name, payload = list(task_obj.items())[0]
                    normalized = _wrap_flat_metrics(payload)
                    results[task_name] = normalized

                if not results:
                    return None

                return {
                    "submission_id": entry.get("submission_id") or str(uuid.uuid4()),
                    "display_name": entry.get("display_name")
                    or entry.get("model_name")
                    or "Unnamed Model",
                    "email": entry.get("email", "N/A"),
                    "results": results,
                }

            # Le fichier peut contenir UNE entrée (dict) ou PLUSIEURS (list)
            if isinstance(data, list):
                for item in data:
                    processed = process_entry(item)
                    if processed:
                        entries.append(processed)
            else:
                processed = process_entry(data)
                if processed:
                    entries.append(processed)

        except Exception as e:
            logging_message = f"Error processing file '{filepath}': {e}"
            logging.error(logging_message)
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
