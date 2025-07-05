import logging
from typing import Dict, Union, Tuple, Callable, List

from datasets import load_dataset

from src.metrics.metric_factory import metric_factory
from src.task import REPOSITORY_NAME


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
        label_cleaning_fn: Callable = None,
    ) -> None:
        self._metric_name = metric
        self._metric_computer = metric_factory(metric_name=self.metric_name)
        self.task_name = task_name
        test_split = load_dataset(
            f"{REPOSITORY_NAME}", name=self.task_name, split="test"
        )[ground_truths_column_name]

        if label_cleaning_fn is not None:
            test_split = label_cleaning_fn(test_split)

        self._ground_truths = test_split

    @property
    def metric_name(self) -> str:
        return self._metric_name

    def compute(self, predictions: Union[List, None]) -> Tuple[Dict, str]:
        warning = None
        if predictions is None:
            # Case were we did not find any prediction for the task.
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
            error = "There is more prediction thant ground truths."
            logging.error(error)
            raise ValueError(error)
        else:
            ground_truths = self._ground_truths

        metric_score = self._metric_computer.compute(
            predictions=predictions, references=ground_truths
        )

        return metric_score, warning
