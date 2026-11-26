# pylint: disable=wrong-import-position,protected-access
import sys
import unittest
from types import ModuleType, SimpleNamespace
from typing import Dict, List
from unittest.mock import patch

from datasets import Dataset

from cole.language_model.open_ai_api_lm_wrapper import OpenAIAPILMWrapper

# The real factory imports every vendor SDK (mistralai, cohere, ...), which the unit tests
# neither need nor call: stub it so RemoteLLMModel can be imported without them.
_FACTORY = "cole.language_model.private_language_model_factory"
if _FACTORY not in sys.modules:
    _stub = ModuleType(_FACTORY)
    _stub.private_language_model_factory = lambda model_name: None
    sys.modules[_FACTORY] = _stub

from cole.language_model.private_lm import (
    RemoteLLMModel,
)  # pylint: disable=wrong-import-position
from cole.task.task import TaskType


def make_completion(content: str) -> SimpleNamespace:
    """Build a minimal chat completion without tool calls."""
    message = SimpleNamespace(content=content, tool_calls=None)
    return SimpleNamespace(choices=[SimpleNamespace(message=message)])


class FakeWrapper(OpenAIAPILMWrapper):
    """Wrapper whose API client is replaced by a scripted list of outcomes."""

    def __init__(self, outcomes: List, **kwargs):
        super().__init__(model_name="gpt-fake", **kwargs)
        self.outcomes = list(outcomes)
        self.calls = 0
        self.seen_params: List[Dict] = []

    def _inner_generate_fn(self, prompt: List) -> Dict:
        self.calls += 1
        self.seen_params.append(dict(self._extra_params))
        outcome = self.outcomes.pop(0) if self.outcomes else self.outcomes_default()
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    @staticmethod
    def outcomes_default():
        return make_completion("default")


@patch("time.sleep", lambda *_: None)
class ExtractiveAnswerTest(unittest.TestCase):
    def test_multi_word_answer_with_colon_keeps_spaces(self):
        wrapper = FakeWrapper(
            [make_completion("Réponse : le roi Louis XIV")], extra_params={}
        )
        result = wrapper.predict("question", extract_label=False)
        self.assertEqual("Réponse : le roi Louis XIV", result["prediction"])

    def test_generative_answer_with_digits_is_not_replaced_by_a_digit(self):
        wrapper = FakeWrapper(
            [make_completion("En 1789 (Révolution)")], extra_params={}
        )
        result = wrapper.predict("question", extract_label=False)
        self.assertEqual("En 1789 (Révolution)", result["prediction"])

    def test_label_extraction_still_works_for_classification(self):
        wrapper = FakeWrapper([make_completion("La réponse est : 1")], extra_params={})
        self.assertEqual("1", wrapper.predict("question")["prediction"])
        wrapper = FakeWrapper([make_completion("Je choisis 2 car")], extra_params={})
        self.assertEqual("2", wrapper.predict("question")["prediction"])

    def test_anthropic_text_blocks_are_read_for_generative_tasks(self):
        blocks = [SimpleNamespace(type="text", text="Louis XIV, roi de France")]
        wrapper = FakeWrapper([SimpleNamespace(content=blocks)], extra_params={})
        wrapper.model_name = "claude-fake"
        result = wrapper.predict("question", extract_label=False)
        self.assertEqual("Louis XIV, roi de France", result["prediction"])

    def test_generative_failure_is_explicit_na_not_minus_one(self):
        wrapper = FakeWrapper(
            [RuntimeError("boom")] * 5, extra_params={}, max_retries=2
        )
        result = wrapper.predict("question", extract_label=False)
        self.assertEqual("NA", result["prediction"])

    def test_classification_failure_stays_castable_minus_one(self):
        wrapper = FakeWrapper(
            [RuntimeError("boom")] * 5, extra_params={}, max_retries=2
        )
        self.assertEqual("-1", wrapper.predict("question")["prediction"])


@patch("time.sleep", lambda *_: None)
class RetryTest(unittest.TestCase):
    def test_retry_returns_result_of_successful_retry(self):
        wrapper = FakeWrapper(
            [RuntimeError("rate limit"), make_completion("Paris")], extra_params={}
        )
        result = wrapper.predict("question", extract_label=False)
        self.assertEqual("Paris", result["prediction"])
        self.assertEqual(2, wrapper.calls)

    def test_retries_are_bounded_and_counted(self):
        wrapper = FakeWrapper(
            [RuntimeError("boom")] * 10, extra_params={}, max_retries=2
        )
        self.assertIsNone(wrapper.language_model_calling([]))
        self.assertEqual(3, wrapper.calls)
        self.assertEqual(
            1, wrapper._max_retries_counter
        )  # pylint: disable=protected-access


class ExtraParamsScopingTest(unittest.TestCase):
    @staticmethod
    def _remote(wrapper: FakeWrapper) -> RemoteLLMModel:
        remote = object.__new__(RemoteLLMModel)
        remote.model = wrapper
        return remote

    def test_generative_task_after_classification_has_no_tools(self):
        base = {"temperature": 0}
        wrapper = FakeWrapper([], extra_params=base)
        remote = self._remote(wrapper)
        dataset = Dataset.from_dict({"text": ["a", "b"]})
        classification = SimpleNamespace(
            task_type=TaskType.INFERENCE,
            task_name="clf",
            dataset=SimpleNamespace(possible_ground_truths=["0", "1"]),
        )
        generative = SimpleNamespace(
            task_type=TaskType.GENERATIVE, task_name="fquad", dataset=None
        )
        remote.predict(dataset, classification)
        self.assertIn("tools", wrapper.seen_params[-1])
        self.assertIn("tool_choice", wrapper.seen_params[-1])

        wrapper.seen_params.clear()
        predictions = remote.predict(dataset, generative)
        self.assertEqual(2, len(predictions))
        for params in wrapper.seen_params:
            self.assertNotIn("tools", params)
            self.assertNotIn("tool_choice", params)
            self.assertEqual(0, params["temperature"])
        # The dict supplied by the caller is never mutated.
        self.assertEqual({"temperature": 0}, base)

    def test_failed_generation_yields_na_row_instead_of_crashing_map(self):
        wrapper = FakeWrapper([], extra_params={}, max_retries=0)
        wrapper.predict = lambda *_args, **_kwargs: (_ for _ in ()).throw(
            RuntimeError()
        )
        remote = self._remote(wrapper)
        dataset = Dataset.from_dict({"text": ["a"]})
        task = SimpleNamespace(
            task_type=TaskType.GENERATIVE, task_name="fquad", dataset=None
        )
        self.assertEqual(["NA"], remote.predict(dataset, task))
