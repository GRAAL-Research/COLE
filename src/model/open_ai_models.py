from typing import Union, List

from src.model.model import Model


class OpenAIModel(Model):

    def infer(
        self, prompts: Union[str, List[str]], possible_answers, conditions=None
    ) -> Union[str, List[str]]:
        pass

    def generate(self, prompts: List[str], conditions=None) -> Union[str, List[str]]:
        pass
