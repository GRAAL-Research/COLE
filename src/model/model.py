# pylint: disable=method-hidden

from abc import abstractmethod, ABC
from typing import Union


class Model(ABC):
    def __init__(self, model_name: str, inference_callback=None, prompt_only=True):
        self.name = model_name
        if inference_callback is not None:
            self.infer = inference_callback
        self.prompt_only = prompt_only

    @abstractmethod
    def infer(
        self, prompts: Union[str, list[str]], possible_answers, conditions=None
    ) -> Union[str, list[str]]:
        raise NotImplementedError

    @abstractmethod
    def generate(self, prompts: list[str], conditions=None) -> Union[str, list[str]]:
        raise NotImplementedError
