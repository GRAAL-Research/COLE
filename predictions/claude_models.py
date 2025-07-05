import os
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv
from lighteval.models.abstract_model import LightevalModel
from lighteval.models.model_output import (
    GenerativeResponse,
    LoglikelihoodResponse,
    LoglikelihoodSingleTokenResponse,
)
from lighteval.tasks.requests import (
    GreedyUntilRequest,
    LoglikelihoodRequest,
    LoglikelihoodRollingRequest,
    LoglikelihoodSingleTokenRequest,
)
from transformers import PreTrainedTokenizerBase

env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("ANTHROPIC_API_KEY")
if api_key is None:
    raise RuntimeError("ANTHROPIC_API_KEY non défini dans .env")

claude_client = Anthropic(api_key=api_key)


class Claude(LightevalModel):

    @property
    def max_length(self) -> int:
        pass

    @property
    def add_special_tokens(self) -> bool:
        pass

    @property
    def tokenizer(self) -> PreTrainedTokenizerBase:
        pass

    def loglikelihood_single_token(
        self, requests: list[LoglikelihoodSingleTokenRequest]
    ) -> list[LoglikelihoodSingleTokenResponse]:
        pass

    def loglikelihood_rolling(
        self, requests: list[LoglikelihoodRollingRequest]
    ) -> list[LoglikelihoodResponse]:
        pass

    def loglikelihood(
        self, requests: list[LoglikelihoodRequest]
    ) -> list[LoglikelihoodResponse]:
        pass

    def greedy_until(
        self, requests: list[GreedyUntilRequest]
    ) -> list[GenerativeResponse]:
        pass


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
