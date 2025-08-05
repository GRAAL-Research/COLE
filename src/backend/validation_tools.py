import logging
from typing import Dict, List

from fastapi import HTTPException

tasks_name = [
    "allocine",
    "fquad",
    "gqnli",
    "paws_x",
    "piaf",
    "qfrblimp",
    "qfrcola",
    "sickfr",
    "sts22",
    "xnli",
]


def validate_submission_template(dictionary: Dict) -> None:
    """Ensures the dictionnary follows the correct format.
    :param dictionary: Dictionary to validate."""
    if dictionary.get("model_name", None) is None:
        error = "The submission is missing a model name."
        logging.error(error)
        raise HTTPException(200, error)
    if dictionary.get("model_url", None) is None:
        error = "The submission is missing a model URL."
        logging.error(error)
        raise HTTPException(200, error)
    if dictionary.get("tasks", None) is None:
        error = "The submission is missing a tasks keyword."
        logging.error(error)
        raise HTTPException(200, error)

    tasks = dictionary.get("tasks")
    if not isinstance(tasks, List):
        error = (
            "The tasks keyword value must be a list of dictionaries where they key is the tasks "
            "and value is a dictionary of predictions (in a list format). See our documentation for"
            "a template."
        )
        logging.error(error)
        raise HTTPException(200, error)

    for task in tasks:
        if len(task.keys()) > 1:
            error = (
                "Each task must be a dictionary of one element where the key is "
                "the task name and the value is a list."
            )
            logging.error(error)
            raise HTTPException(200, error)


def validate_submission_tasks_name(dictionary: Dict) -> None:
    """
    Validate if the submission JSON key are the tasks name.
    """
    for task in dictionary.get("tasks"):
        key = list(task.keys())[0]
        if key not in tasks_name:
            error = f"Unknown key '{key}' in the submission JSON. The expected tasks are: {tasks_name}."
            logging.error(error)
            raise HTTPException(200, error)


def validate_submission_json(dictionary: Dict) -> None:
    """Validates that the submitted json is in the correct format.
    :param dictionary: Dictionary to validate."""
    task_payload = dictionary.get("tasks")

    for task in task_payload:
        for task_name, payload in task.items():
            if not isinstance(payload, dict):
                error = (
                    "The tasks payload must be a dictionary in the format '{'prediction': [<predictions>]}' "
                    "for each task."
                )
                logging.error(error)
                raise HTTPException(200, error)
            for key, value in payload.items():
                if key not in ["predictions", "prediction"]:
                    error = f"The task '{task_name}' payload does not have the expected key: 'predictions'."
                    logging.error(error)
                    raise HTTPException(200, error)
                if not isinstance(value, list):
                    error = (
                        f"The task '{task_name}' predictions payload is not in a list format. "
                        r"The expected format is: '{'prediction': [<predictions>]}'"
                    )
                    logging.error(error)
                    raise HTTPException(200, error)
