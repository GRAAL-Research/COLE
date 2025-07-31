import logging
from typing import Dict, List, Union

from src.task.task import Task, TaskType


def tasks_factory(task_names: Union[Dict, List[str]]) -> List[Task]:
    """
    Factory method to create a list of Task objects from a dictionary of task names and their predictions.
    """
    tasks = []
    if isinstance(task_names, Dict):
        tasks_names = task_names.get("tasks")
        task_names = [list(task.keys())[0] for task in tasks_names]

    for task_name in task_names:
        match task_name:
            case "allocine":
                tasks.append(
                    Task(
                        task_name=task_name,
                        metric="accuracy",
                        task_type=TaskType.INFERENCE,
                    )
                )
            case "fquad":
                tasks.append(
                    Task(
                        task_name=task_name,
                        metric="fquad",
                        task_type=TaskType.GENERATIVE,
                    )
                )
            case "gqnli":
                tasks.append(
                    Task(
                        task_name=task_name,
                        metric="accuracy",
                        task_type=TaskType.INFERENCE,
                    )
                )
            case "paws_x":
                tasks.append(
                    Task(
                        task_name=task_name,
                        metric="accuracy",
                        task_type=TaskType.INFERENCE,
                    )
                )
            case "piaf":
                tasks.append(
                    Task(
                        task_name=task_name,
                        metric="fquad",
                        task_type=TaskType.GENERATIVE,
                    )
                )
            case "qfrblimp":
                tasks.append(
                    Task(
                        task_name=task_name,
                        metric="accuracy",
                        task_type=TaskType.INFERENCE,
                    )
                )
            case "qfrcola":
                tasks.append(
                    Task(
                        task_name=task_name,
                        metric="accuracy",
                        task_type=TaskType.INFERENCE,
                    )
                )
            case "sickfr":
                tasks.append(
                    Task(
                        task_name=task_name,
                        metric="accuracy",
                        task_type=TaskType.INFERENCE,
                    )
                )
            case "sts22":
                tasks.append(
                    Task(
                        task_name=task_name,
                        metric="accuracy",
                        task_type=TaskType.INFERENCE,
                    )
                )
            case "xnli":
                tasks.append(
                    Task(
                        task_name=task_name,
                        metric="accuracy",
                        task_type=TaskType.INFERENCE,
                    )
                )
            case "qfrcore":
                tasks.append(
                    Task(
                        task_name=task_name,
                        metric="accuracy",
                        task_type=TaskType.INFERENCE,
                    )
                )
            case "qfrcort":
                tasks.append(
                    Task(
                        task_name=task_name,
                        metric="accuracy",
                        task_type=TaskType.INFERENCE,
                    )
                )
            case "daccord":
                tasks.append(
                    Task(
                        task_name=task_name,
                        metric="accuracy",
                        task_type=TaskType.INFERENCE,
                    )
                )
            case "french_boolq":
                tasks.append(
                    Task(
                        task_name=task_name,
                        metric="accuracy",
                        task_type=TaskType.INFERENCE,
                    )
                )
            case "mnli-nineeleven-fr-mt":
                tasks.append(
                    Task(
                        task_name=task_name,
                        metric="accuracy",
                        task_type=TaskType.INFERENCE,
                    )
                )
            case "rte3-french":
                tasks.append(
                    Task(
                        task_name=task_name,
                        metric="accuracy",
                        task_type=TaskType.INFERENCE,
                    )
                )
            case "rte3-french":
                tasks.append(
                    Task(
                        task_name=task_name,
                        metric="accuracy",
                        task_type=TaskType.INFERENCE,
                    )
                )
            case "wino_x_lm":
                tasks.append(
                    Task(
                        task_name=task_name,
                        metric="accuracy",
                        task_type=TaskType.INFERENCE,
                    )
                )
            case "wino_x_mt":
                tasks.append(
                    Task(
                        task_name=task_name,
                        metric="accuracy",
                        task_type=TaskType.INFERENCE,
                    )
                )
            case "multiblimp":
                tasks.append(
                    Task(
                        task_name=task_name,
                        metric="accuracy",
                        task_type=TaskType.INFERENCE,
                    )
                )
            case "fracas":
                tasks.append(
                    Task(
                        task_name=task_name,
                        metric="accuracy",
                        task_type=TaskType.INFERENCE,
                    )
                )
            case "mms":
                tasks.append(
                    Task(
                        task_name=task_name,
                        metric="accuracy",
                        task_type=TaskType.INFERENCE,
                    )
                )
            case _:
                error = f"Unknown task {task_name}."
                logging.error(error)
                raise ValueError(error)
    return tasks
