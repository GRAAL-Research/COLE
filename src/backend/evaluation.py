import copy
import operator
from functools import reduce
from typing import List, Dict

from src.task.task_factory import Task


def compute_tasks_ratings(tasks: List[Task], submission: Dict) -> Dict:
    """
    Method to compute the tasks ratings.
    :param tasks: list of tasks
    :param submission: submission dictionary
    """

    # We merge the tasks dictionary for simpler handling.
    submission_copy = copy.deepcopy(submission)
    submission_response = reduce(operator.ior, submission_copy.get("tasks"), {})

    for task in tasks:
        task_name = task.task_name

        # We remove the prediction since we do not keep it in the response.
        # Validation allows both "predictions" and "prediction"; pop whichever is present.
        task_payload = submission_response.get(task_name)
        if "predictions" in task_payload:
            predictions = task_payload.pop("predictions")
        else:
            predictions = task_payload.pop("prediction")

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
