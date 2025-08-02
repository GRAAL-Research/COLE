# pylint: disable=inconsistent-return-statements
import time
from abc import ABC, abstractmethod
from typing import List, Dict

from src.language_model.init_function_calling import init_function_calling


class OpenAIAPILMWrapper(ABC):
    def __init__(
        self,
        model_name: str,
        extra_params: Dict,
        use_function_calling: bool = True,
        max_retries: int = 10,
    ):
        self.model_name = model_name
        self._extra_params = extra_params
        self.max_retries = max_retries
        self.use_function_calling = use_function_calling
        self.tool_choices = "required"

    def init_function_calling(self, labels: List[str], tool_choices: str) -> None:
        if self.use_function_calling:
            self._extra_params.update(
                init_function_calling(labels=labels, tool_choices=tool_choices)
            )

    @abstractmethod
    def _inner_generate_fn(self, prompt: List) -> Dict:
        pass

    @staticmethod
    def format_prompt(text: str) -> List:
        return [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": text},
                ],
            }
        ]

    def language_model_calling(self, prompt: List):
        return self._try_again(prompt=prompt)

    def _try_again(self, prompt: List, retries: int = 0):
        generated_completion = None
        if retries > self.max_retries:
            return generated_completion
        try:
            generated_completion = self._inner_generate_fn(prompt=prompt)
            return generated_completion
        except:
            time.sleep(5)
            self._try_again(prompt=prompt, retries=retries + 1)
