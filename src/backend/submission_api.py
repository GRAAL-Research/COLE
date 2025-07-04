import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Any
from uuid import uuid4

from fastapi import FastAPI, UploadFile, Form, File
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from src.backend.evaluation_pipeline import evaluation_submission
from src.backend.model import ZipInferenceModel
from src.backend.submit_tools import (
    load_predictions_from_zip,
    convert_custom_dict_to_task_dict,
    predictions_logging,
    get_max_samples,
    get_tasks_as_str,
    log_per_example_results,
    extract_aggregated_metrics,
    build_output_json,

)

logging.getLogger("lighteval").setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# --- Paths configuration ---
BASE_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = BASE_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

RESULTS_DIR = BASE_DIR / "src" / "backend" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

import src.tasks_custom as tasks_module

from lighteval.logging.evaluation_tracker import EvaluationTracker
from lighteval.pipeline import Pipeline, PipelineParameters, ParallelismManager

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
    raw_dict = load_predictions_from_zip(zip_bytes)

    tasks_prediction_dictionary = convert_custom_dict_to_task_dict(raw_dict)

    predictions_logging(tasks_prediction_dictionary)

    max_samples = get_max_samples(
        tasks_prediction_dictionary=tasks_prediction_dictionary
    )
    logging.info(f"Using 'max_samples={max_samples}' in pipeline parameters.")

    task_str, available_tasks = get_tasks_as_str(
        tasks_prediction_dictionary=tasks_prediction_dictionary
    )

    results_tracker = EvaluationTracker(
        output_dir=str(RESULTS_DIR / "temp"), save_details=True, push_to_hub=False
    )

    pipeline_parameters = PipelineParameters(
        launcher_type=ParallelismManager.ACCELERATE,
        custom_tasks_directory=tasks_module,
        max_samples=max_samples,
    )

    model = ZipInferenceModel(tasks_prediction_dictionary)

    evaluation_submission(
        task_str=task_str,
        results_tracker=results_tracker,
        pipeline_parameters=pipeline_parameters,
        model=model,
    )

    log_per_example_results(results_tracker)

    results = extract_aggregated_metrics(results_tracker)

    output = build_output_json(
        email=email,
        display_name=display_name,
        predictions_zip_filename=predictions_zip.filename,
        results=results,
        tasks_prediction_dictionary=tasks_prediction_dictionary,
        available_tasks=available_tasks,
        max_samples=max_samples,
    )

    out_path = RESULTS_DIR / f"{output['config_general']['submission_id']}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    return JSONResponse(content=output)


@app.get("/leaderboard")
async def leaderboard() -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    for fn in sorted(os.listdir(RESULTS_DIR)):
        if not fn.endswith(".json"):
            continue
        with open(RESULTS_DIR / fn, encoding="utf-8") as f:
            data = json.load(f)

        cfg = data["config_general"]
        global_metrics = data.get("results", {}).get("all", {})
        acc = global_metrics.get("acc")
        score_pct = None
        if isinstance(acc, (int, float)):
            score_pct = round(acc * 100, 1)

        entries.append(
            {
                "submission_id": cfg["submission_id"],
                "display_name": cfg["display_name"],
                "score": score_pct,  # global
                "results": data.get("results", {}),  # ← on ajoute ça
            }
        )

    return entries


@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}