import io
import json
import logging
import zipfile
from http.client import HTTPException
from typing import Dict, List, Tuple, Any
from uuid import uuid4

from fastapi import HTTPException
from lighteval.logging.evaluation_tracker import EvaluationTracker

from src.tasks_custom import BASE_TASKS


def convert_custom_dict_to_task_dict(dictionary: Dict) -> Dict:
    """
    Converts a custom dictionary in the format '{"custom|TASK|0|0": a_list}' into the format
    '{"TASK": a_list}'.
    """
    for k, v in dictionary.items():
        if "custom" not in k:
            error_msg = "The dictionary is not formated as expected, a task should be written as 'custom|TASK|0|0'."
            logging.error(error_msg)
            raise ValueError(error_msg)
        elif len(k.split("|")) < 4:
            error_msg = "The dictionary is not formated as expected, a task should be written as 'custom|TASK|0|0'."
            logging.error(error_msg)
            raise ValueError(error_msg)

    return {k.split("|")[1]: v for k, v in dictionary.items()}


def predictions_logging(task_prediction_dictionary: Dict) -> None:
    logging.info("=== Loaded predictions ===")
    for t, vals in task_prediction_dictionary.items():
        logging.info(f"  {t}: {vals}")


def get_max_samples(tasks_prediction_dictionary: Dict) -> int:
    return (
        len(next(iter(tasks_prediction_dictionary.values())))
        if tasks_prediction_dictionary
        else 0
    )


def get_tasks_as_str(tasks_prediction_dictionary: Dict) -> Tuple[str, List]:
    available_tasks = [t for t in BASE_TASKS if t in tasks_prediction_dictionary]
    if not available_tasks:
        raise HTTPException(400, "Aucune tâche reconnue dans predictions.json.")
    task_str = ",".join(f"custom|{t}|0|0" for t in available_tasks)
    logging.info(f"Evaluating tasks: {task_str}")

    return task_str, available_tasks


def unzip_predictions_from_zip(zip_bytes: bytes) -> dict:
    """
    Reads predictions.json directly from the ZIP in memory.
    """
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        if "predictions.json" not in z.namelist():
            raise HTTPException(400, "Le ZIP ne contient pas predictions.json.")
        with z.open("predictions.json") as f:
            return json.load(f)

def log_per_example_results(tracker: EvaluationTracker) -> None:
    details = tracker.results.get("details", {})
    print("=== Per-example (gold vs pred) ===")

    for full_task, info in details.items():
        parts = full_task.split("|")
        short = parts[1] if len(parts) > 1 else parts[0]
        print(f"--- Task {short} ---")

        for ex in info.get("examples", []):
            print(f"   gold={ex['gold']!r}  pred={ex['pred']!r}")


def extract_aggregated_metrics(tracker: EvaluationTracker) -> Dict[str, Dict[str, Any]]:
    raw = tracker.results.get("results", {})
    results: Dict[str, Dict[str, Any]] = {}
    logging.info("=== Aggregated metrics ===")

    for full_task, metrics in raw.items():
        parts = full_task.split("|")
        short = parts[1] if len(parts) > 1 else parts[0]
        filtered = {k: v for k, v in metrics.items() if isinstance(v, (int, float))}
        results[short] = filtered
        logging.info(f"  {short}: {filtered}")

    return results


def build_output_json(
    email: str,
    display_name: str,
    predictions_zip_filename: str,
    results: Dict[str, Dict[str, Any]],
    tasks_prediction_dictionary: Dict[str, List[Any]],
    available_tasks: List[str],
    max_samples: int,
) -> Dict[str, Any]:
    output = {
        "config_general": {
            "submission_id": str(uuid4()),
            "email": email,
            "display_name": display_name,
            "zip_filename": predictions_zip_filename,
        },
        "results": results,
        "predictions": {
            t: tasks_prediction_dictionary[t][:max_samples] for t in available_tasks
        },
    }

    return output