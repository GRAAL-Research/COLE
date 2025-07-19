import logging
from typing import Dict, List, Union

from src.task.task import Task, Tasktype


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
                    )
                )
            case "fquad":
                tasks.append(
                    Task(
                        task_name=task_name,
                        metric="fquad",
                        task_type=Tasktype.GENERATIVE,
                    )
                )
            case "gqnli":
                tasks.append(
                    Task(
                        task_name=task_name,
                        metric="accuracy",
                    )
                )
            case "opus_parcus":
                tasks.append(
                    Task(
                        task_name=task_name,
                        metric="pearson",
                    )
                )
            case "paws_x":
                tasks.append(
                    Task(
                        task_name=task_name,
                        metric="accuracy",
                    )
                )
            case "piaf":
                tasks.append(
                    Task(
                        task_name=task_name,
                        metric="fquad",
                        task_type=Tasktype.GENERATIVE,
                    )
                )
            case "qfrblimp":
                tasks.append(
                    Task(
                        task_name=task_name,
                        metric="accuracy",
                    )
                )
            case "qfrcola":
                tasks.append(
                    Task(
                        task_name=task_name,
                        metric="accuracy",
                    )
                )
            case "sickfr":
                tasks.append(
                    Task(
                        task_name=task_name,
                        metric="pearson",
                    )
                )
            case "sts22":
                tasks.append(
                    Task(
                        task_name=task_name,
                        metric="pearson",
                    )
                )
            case "xnli":
                tasks.append(
                    Task(
                        task_name=task_name,
                        metric="accuracy",
                    )
                )
            case "expressions_quebecoises":
                tasks.append(
                    Task(
                        task_name=task_name,
                        metric="accuracy",
                    )
                )
            case _:
                error = f"Unknown task {task_name}."
                logging.error(error)
                raise ValueError(error)
    return tasks
