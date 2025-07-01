from http.client import HTTPException
from typing import Dict, List, Tuple
import logging

from src.light_eval_custom import BASE_TASKS


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
