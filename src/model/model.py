# pylint: disable=method-hidden

from abc import abstractmethod, ABC
from typing import Union, List

from datasets import Dataset

from src.task.task import Task


class Model(ABC):
    def __init__(self, model_name: str, inference_callback=None, prompt_only=True):
        self.name = model_name
        if inference_callback is not None:
            self.infer = inference_callback
        self.prompt_only = prompt_only

    @abstractmethod
    def predict(self, evaluation_dataset: Dataset, task: Task) -> List:
        raise NotImplementedError

    @abstractmethod
    def infer(self, rows: List[str]) -> Union[str, List[str]]:
        raise NotImplementedError

    @abstractmethod
    def generate(self, rows: List[str]) -> Union[str, List[str]]:
        raise NotImplementedError
