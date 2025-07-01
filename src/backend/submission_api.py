import io
import json
import logging
import math
import os
import sys
import zipfile
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, UploadFile, Form, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from src.backend.submit_tools import get_customs_keys, convert_custom_dict_to_task_dict

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
import src.light_eval_custom.tasks as tasks_module

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


def load_predictions_from_zip(zip_bytes: bytes) -> dict:
    """Lit directement predictions.json depuis le ZIP en mémoire."""
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        if "predictions.json" not in z.namelist():
            raise HTTPException(400, "Le ZIP ne contient pas predictions.json.")
        with z.open("predictions.json") as f:
            return json.load(f)


class DummyResponse:
    def __init__(self, idx: int, choices: list, prompt: str):
        self.result = [choices[idx] if 0 <= idx < len(choices) else choices[0]]
        self.generated_tokens = self.result
        self.input_tokens = [prompt]
        self.truncated_tokens_count = 0
        self.padded_tokens_count = 0
        hp, lp = 0.9, 0.1
        self.choice_logprobs = [
            math.log(hp) if i == idx else math.log(lp) for i in range(len(choices))
        ]
        self.logprobs = [self.choice_logprobs[idx]]

    def get_result_for_eval(self) -> str:
        return self.result[0]


class ZipInferenceModel:
    is_async = False

    def __init__(self, predictions: dict):
        # predictions: {"allocine": [...], ...}
        self._predictions = predictions

    def infer(self, requests, conditions=None):
        # extraire task_name complet, p.ex. "custom|allocine|0|0"
        raw = (
            conditions[0].task_name
            if conditions and hasattr(conditions[0], "task_name")
            else getattr(requests[0], "task_name", None)
        )
        # short = le nom entre les pipes
        short = raw.split("|")[1] if raw and "|" in raw else raw

        vals = self._predictions.get(short, [])
        if not isinstance(vals, list):
            vals = [vals]

        logging.info(f"[INFER] Task={short}, JSON vals (len={len(vals)}): {vals}")

        outputs = []
        for i, req in enumerate(requests):
            prompt = getattr(req, "prompt", getattr(req, "query", str(req)))
            try:
                idx = int(vals[i])
            except Exception:
                idx = 0
            choices = getattr(req, "choices", ["0", "1"])
            if idx >= len(choices):
                idx = 0
            outputs.append(DummyResponse(idx, choices, prompt))

        preds = [o.get_result_for_eval() for o in outputs]
        logging.info(f"[INFER] Task={short}, Generated preds: {preds}")
        return outputs

    def get_method_from_request_type(self, request_type):
        return self.infer

    def cleanup(self):
        pass


@app.post("/submit")
async def submit(
    email: str = Form(...),
    predictions_zip: UploadFile = File(...),
    display_name: str = Form(...),
):
    logging.info(f"Submission from {email!r} as {display_name!r}.")

    zip_bytes = await predictions_zip.read()
    raw_dict = load_predictions_from_zip(zip_bytes)

    all_preds = convert_custom_dict_to_task_dict(raw_dict)

    logging.info("=== Loaded predictions ===")
    for t, vals in all_preds.items():
        logging.info(f"  {t}: {vals}")

    # 3) Déterminer N
    N = len(next(iter(all_preds.values()))) if all_preds else 0
    logging.info(f"Using max_samples = {N}")

    # 4) Préparer tasks
    base_tasks = [
        "allocine",
        "paws_x",
        "fquad",
        "gqnli",
        "piaf",
        "sickfr",
        "xnli",
        "frcola",
        "frblimp",
        "sts22",
    ]
    available = [t for t in base_tasks if t in all_preds]
    if not available:
        raise HTTPException(400, "Aucune tâche reconnue dans predictions.json.")
    task_str = ",".join(f"custom|{t}|0|0" for t in available)
    logging.info(f"Evaluating tasks: {task_str}")

    # 5) Configurer l’évaluation
    tracker = EvaluationTracker(
        output_dir=str(RESULTS_DIR / "temp"), save_details=True, push_to_hub=False
    )
    params = PipelineParameters(
        launcher_type=ParallelismManager.ACCELERATE,
        custom_tasks_directory=tasks_module,
        max_samples=N,
    )
    config = TransformersModelConfig(
        model_name="bert-base-uncased",
        dtype="auto",
        use_chat_template=True,
        device="cpu",
        batch_size=1,
    )
    pipeline = Pipeline(
        tasks=task_str,
        pipeline_parameters=params,
        evaluation_tracker=tracker,
        model_config=config,
    )
    pipeline.model = ZipInferenceModel(all_preds)

    # 6) Lancer l’évaluation
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
        "predictions": {t: all_preds[t][:N] for t in available},
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
