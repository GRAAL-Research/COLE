import logging
import operator
from functools import reduce
from typing import List, Dict

from fastapi import HTTPException

from src.task.task_factory import Task


def compute_tasks_ratings(tasks: List[Task], submission: Dict) -> Dict:
    """
    Method to compute the tasks ratings.
    """

    # We merge the tasks dictionary for simpler handling.
    submission_response = reduce(operator.ior, submission.get("tasks"), {})
    for task in tasks:
        task_name = task.task_name
        predictions = submission_response.get(task_name, None)
        if predictions is None:
            error = f"Task {task_name} has no predictions"
            logging.error(error)
            raise HTTPException(200, error)

        ratings, warning = task.compute(predictions=predictions)
        ratings.update({f"{task.metric_name}_warning": warning})
        submission_response.get(task_name).update({f"{task.metric_name}": ratings})

    # Final submission response where we unwrap the merge tasks dictionary into a list of dictionary.
    submission_response = {
        "model_name": submission.get("model_name"),
        "model_url": submission.get("model_url"),
        "tasks": [{key: value} for key, value in submission_response.items()],
    }
    return submission_response
