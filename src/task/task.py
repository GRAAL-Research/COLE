import logging
from enum import Enum
from typing import Dict, Union, Tuple, Callable, List
from src.metrics.metric_factory import metric_factory
from src.dataset.datasets import datasets

class Tasktype(Enum):
    GENERATIVE = 0
    INFERENCE = 1

class Task:
    """
    Class representing a task to be executed.

    :param: name (str): The name of the task.
    :param: metric (str): The name of the metric to use.
    :param: ground_truths_column_name (str): The ground truths column name in the dataset.
    """

    def __init__(
        self,
        task_name: str,
        metric: str,
        ground_truths_column_name: str,
        llm_prompt_building_fn: Callable = None,
        task_type: Tasktype = Tasktype.INFERENCE,
    ) -> None:
        self._metric_name = metric
        self._metric_computer = metric_factory(metric_name=self.metric_name)
        self.task_name = task_name
        self.dataset = datasets[task_name]
        self._ground_truths = self.dataset.ground_truths
        self.task_type = task_type

    @property
    def metric_name(self) -> str:
        return self._metric_name

    def compute(self, predictions: Union[List, None]) -> Tuple[Dict, str]:
        warning = None
        if predictions is None:
            # Case where we did not find any prediction for the task.
            warning = "No predictions found for this task."
            return {self.metric_name: 0.0}, warning

        sample_size = len(predictions)

        if sample_size < len(self._ground_truths):
            # Means we have a sample of the prediction
            ground_truths = self._ground_truths[:sample_size]
            warning = (
                f"Your prediction size is of '{sample_size}', while the ground truths size is "
                f"of '{len(self._ground_truths)}'. We computed the metric over the first "
                f"{sample_size} elements."
            )
        elif sample_size > len(self._ground_truths):
            error = "There are more predictions than ground truths."
            logging.error(error)
            raise ValueError(error)
        else:
            ground_truths = self._ground_truths

        metric_score = self._metric_computer.compute(
            predictions=predictions, references=ground_truths
        )

        return metric_score, warning
