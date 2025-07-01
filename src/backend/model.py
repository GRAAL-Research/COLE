import logging
import math

from lighteval.models.abstract_model import LightevalModel, ModelInfo
from lighteval.models.model_output import (
    LoglikelihoodSingleTokenResponse,
    LoglikelihoodResponse,
    GenerativeResponse,
)
from lighteval.tasks.requests import (
    LoglikelihoodSingleTokenRequest,
    LoglikelihoodRollingRequest,
    LoglikelihoodRequest,
    GreedyUntilRequest,
)
from transformers import PreTrainedTokenizerBase


class DummyResponse:
    def __init__(self, idx: int, choices: list, prompt: str):
        self.result = [choices[idx] if 0 <= idx < len(choices) else choices[0]]
        self.generated_tokens = self.result
        self.input_tokens = [prompt]
        self.truncated_tokens_count = 0
        self.padded_tokens_count = 0
        hp, lp = 0.9, 0.1
        self.choice_logprobs = [
            math.log(hp) if i == idx else math.log(lp) for i in range(len(choices))
        ]
        self.logprobs = [self.choice_logprobs[idx]]

    def get_result_for_eval(self) -> str:
        return self.result[0]


class ZipInferenceModel(LightevalModel):
    """
    Model to be use in LightEval evaluation pipeline.
    We use the abstract LightevalModel class and fakely override abstract method.
    """

    is_async = False

    def __init__(self, predictions: dict):
        # predictions: {"allocine": [...], ...}
        self._predictions = predictions

    def infer(self, requests, conditions=None):
        # extraire task_name complet, p.ex. "custom|allocine|0|0"
        raw = (
            conditions[0].task_name
            if conditions and hasattr(conditions[0], "task_name")
            else getattr(requests[0], "task_name", None)
        )
        # short = le nom entre les pipes
        short = raw.split("|")[1] if raw and "|" in raw else raw

        vals = self._predictions.get(short, [])
        if not isinstance(vals, list):
            vals = [vals]

        logging.info(f"[INFER] Task={short}, JSON vals (len={len(vals)}): {vals}")

        outputs = []
        for i, req in enumerate(requests):
            prompt = getattr(req, "prompt", getattr(req, "query", str(req)))
            try:
                idx = int(vals[i])
            except Exception:
                idx = 0
            choices = getattr(req, "choices", ["0", "1"])
            if idx >= len(choices):
                idx = 0
            outputs.append(DummyResponse(idx, choices, prompt))

        preds = [o.get_result_for_eval() for o in outputs]
        logging.info(f"[INFER] Task={short}, Generated preds: {preds}")
        return outputs

    def get_method_from_request_type(self, request_type):
        return self.infer

    def cleanup(self):
        pass

    @property
    def model_info(self):
        return ModelInfo(
            self.__str__(),
            model_sha=str(hash(self.__str__())),
            model_dtype=None,
            model_size=None,
        )

    @property
    def add_special_tokens(self) -> bool:
        pass

    @property
    def max_length(self) -> int:
        pass

    def greedy_until(
        self, requests: list[GreedyUntilRequest]
    ) -> list[GenerativeResponse]:
        pass

    def loglikelihood(
        self, requests: list[LoglikelihoodRequest]
    ) -> list[LoglikelihoodResponse]:
        pass

    def loglikelihood_rolling(
        self, requests: list[LoglikelihoodRollingRequest]
    ) -> list[LoglikelihoodResponse]:
        pass

    def loglikelihood_single_token(
        self, requests: list[LoglikelihoodSingleTokenRequest]
    ) -> list[LoglikelihoodSingleTokenResponse]:
        pass

    @property
    def tokenizer(self) -> PreTrainedTokenizerBase:
        pass
