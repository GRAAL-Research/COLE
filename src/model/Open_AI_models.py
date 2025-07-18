from typing import Union

from src.model.model import Model


class OpenAIModel(Model):

    def infer(
        self, prompts: Union[str, list[str]], possible_answers, conditions=None
    ) -> Union[str, list[str]]:
        pass

    def generate(self, prompts: list[str], conditions=None) -> Union[str, list[str]]:
        pass
