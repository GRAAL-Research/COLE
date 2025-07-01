import json
import logging
import os
import sys
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, UploadFile, Form, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from src.backend.model import ZipInferenceModel
from src.backend.submit_tools import (
    convert_custom_dict_to_task_dict,
    predictions_logging,
    get_max_samples,
    get_tasks_as_str,
    load_predictions_from_zip,
)

# --- Logs suppressions of LightEval ---
logging.getLogger("lighteval").setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# --- Paths configuration ---
BASE_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = BASE_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

RESULTS_DIR = BASE_DIR / "src" / "backend" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# --- Imports LightEval & FastAPI ---
import src.light_eval_custom.custom_metrics as custom_metrics

custom_metrics.add_custom_metrics_to_lighteval()

import src.tasks_custom as tasks_module

from lighteval.logging.evaluation_tracker import EvaluationTracker
from lighteval.pipeline import Pipeline, PipelineParameters, ParallelismManager
from lighteval.models.transformers.transformers_model import TransformersModelConfig

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

    tracker = EvaluationTracker(
        output_dir=str(RESULTS_DIR / "temp"), save_details=True, push_to_hub=False
    )

    params = PipelineParameters(
        launcher_type=ParallelismManager.ACCELERATE,
        custom_tasks_directory=tasks_module,
        max_samples=max_samples,
    )

    pipeline = Pipeline(
        tasks=task_str,
        pipeline_parameters=params,
        evaluation_tracker=tracker,
        model=ZipInferenceModel(tasks_prediction_dictionary),
    )

    pipeline.evaluate()

    # 7) Logger paire à paire (gold/pred)
    details = tracker.results.get("details", {})
    logging.info("=== Per-example (gold vs pred) ===")
    for full_task, info in details.items():
        # extraction safe du nom court
        parts = full_task.split("|")
        short = parts[1] if len(parts) > 1 else parts[0]
        logging.info(f"--- Task {short} ---")
        for ex in info.get("examples", []):
            logging.info(f"   gold={ex['gold']!r}  pred={ex['pred']!r}")

    # 8) Récupérer et afficher métriques agrégées
    raw = tracker.results.get("results", {})
    results = {}
    logging.info("=== Aggregated metrics ===")
    for full_task, metrics in raw.items():
        parts = full_task.split("|")
        short = parts[1] if len(parts) > 1 else parts[0]
        filtered = {k: v for k, v in metrics.items() if isinstance(v, (int, float))}
        results[short] = filtered
        logging.info(f"  {short}: {filtered}")

    # 9) Construire le JSON de sortie
    output = {
        "config_general": {
            "submission_id": str(uuid4()),
            "email": email,
            "display_name": display_name,
            "zip_filename": predictions_zip.filename,
        },
        "results": results,
        "predictions": {
            t: tasks_prediction_dictionary[t][:max_samples] for t in available_tasks
        },
    }

    out_path = RESULTS_DIR / f"{output['config_general']['submission_id']}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    return FileResponse(
        str(out_path), media_type="application/json", filename=out_path.name
    )


@app.get("/leaderboard")
async def leaderboard():
    entries = []
    for fn in sorted(os.listdir(RESULTS_DIR)):
        if fn.endswith(".json"):
            with open(RESULTS_DIR / fn, encoding="utf-8") as f:
                data = json.load(f)
            entries.append(data["config_general"])
    return JSONResponse({"leaderboard": entries})


@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}
