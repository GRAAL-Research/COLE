import logging
import os
from abc import abstractmethod
from pathlib import Path
from typing import Union

from anthropic import Anthropic

from dotenv import load_dotenv

env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("ANTHROPIC_API_KEY")
if api_key is None:
    warning_message = "Couldn't find an API key for Anthropic API"
    logging.warning(warning_message)
else:
    claude_client = Anthropic(api_key=api_key)


def make_claude_inference(model_name: str):
    def infer(prompt: str) -> str:
        response = claude_client.messages.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512,
            temperature=0.0,
        )
        # Extraire uniquement le texte de la réponse
        return response.content[0].text.strip() if response.content else ""

    return infer


class Model:
    def __init__(self, model_name: str, inference_callback=None, prompt_only=True):
        self.name = model_name
        if inference_callback is not None:
            self.infer = inference_callback
        self.prompt_only = prompt_only

    @abstractmethod
    def infer(
        self, prompts: Union[str, list[str]], possible_answers, conditions=None
    ) -> Union[str, list[str]]:
        return ["0" for _ in range(len(prompts))]

    @abstractmethod
    def generate(self, prompts: list[str], conditions=None) -> Union[str, list[str]]:
        raise NotImplementedError()

    def unload_model(self):
        pass
