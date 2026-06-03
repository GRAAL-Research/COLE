"""Tests for ModelEvaluator that do not require HF dataset access.

`compute_metrics` with an empty tasks list never reaches `tasks_factory`,
so we can exercise the response-shape and aliasing fix without HF_TOKEN.
`save_object` is filesystem-only.
"""

import json
import os
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest import mock

from cole.evaluation.llm_evaluator import ModelEvaluator


class ComputeMetricsAliasingTest(TestCase):
    @mock.patch("cole.evaluation.llm_evaluator.wandb")
    def test_does_not_alias_last_predictions(self, _wandb_mock):
        # Previously `compute_metrics` ended with
        #   self.last_metrics = self.last_predictions
        # so mutating `last_metrics` would silently mutate `last_predictions`.
        evaluator = ModelEvaluator()
        evaluator.last_predictions = {
            "model_name": "x",
            "model_url": "u",
            "tasks": [],
        }

        evaluator.compute_metrics()

        # Sanity: the response carries the predictions metadata over.
        self.assertEqual("x", evaluator.last_metrics["model_name"])
        self.assertEqual("u", evaluator.last_metrics["model_url"])
        # Critical: the two are NOT the same object.
        self.assertIsNot(evaluator.last_metrics, evaluator.last_predictions)
        # Critical: mutating one does not bleed into the other.
        evaluator.last_metrics["tasks"].append("MUTATED")
        self.assertEqual([], evaluator.last_predictions["tasks"])


class SaveMetricsGuardTest(TestCase):
    def test_returns_none_when_nothing_to_save(self):
        # The previous `if self.last_metrics is None` check never fired
        # because `__init__` sets `last_metrics = {}`. Now both empty
        # and None are handled.
        evaluator = ModelEvaluator()
        # `__init__` leaves last_metrics == {} and last_model_name == None.
        result = evaluator.save_metrics("/tmp/should-not-be-created")
        self.assertIsNone(result)
        self.assertFalse(os.path.exists("/tmp/should-not-be-created"))

    def test_returns_none_when_model_name_missing(self):
        evaluator = ModelEvaluator()
        evaluator.last_metrics = {"some": "data"}
        # last_model_name is still None: previously this would AttributeError
        # on `self.last_model_name.replace(...)`.
        result = evaluator.save_metrics("/tmp/should-not-be-created")
        self.assertIsNone(result)


class SaveObjectTest(TestCase):
    def setUp(self):
        self.evaluator = ModelEvaluator()

    def test_creates_new_file_with_payload(self):
        with TemporaryDirectory() as tmp:
            payload = {"model_name": "m", "tasks": [{"qfrcola": [0, 1]}]}
            path = self.evaluator.save_object(tmp, payload, "out.json")
            with open(path, encoding="utf-8") as f:
                self.assertEqual(payload, json.load(f))

    def test_appends_tasks_when_file_exists(self):
        with TemporaryDirectory() as tmp:
            existing = {"model_name": "m", "tasks": [{"a": 1}]}
            path = os.path.join(tmp, "out.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(existing, f)

            new_payload = {"model_name": "m", "tasks": [{"b": 2}]}
            self.evaluator.save_object(tmp, new_payload, "out.json")

            with open(path, encoding="utf-8") as f:
                merged = json.load(f)
            self.assertEqual([{"a": 1}, {"b": 2}], merged["tasks"])

    def test_existing_file_without_tasks_key_does_not_crash(self):
        # Previously `data.get("tasks").extend(...)` would AttributeError
        # on a legacy/malformed file that has no "tasks" key.
        with TemporaryDirectory() as tmp:
            existing = {"model_name": "m"}  # no "tasks" key
            path = os.path.join(tmp, "out.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(existing, f)

            new_payload = {"model_name": "m", "tasks": [{"a": 1}]}
            self.evaluator.save_object(tmp, new_payload, "out.json")

            with open(path, encoding="utf-8") as f:
                merged = json.load(f)
            # The new tasks were merged in, no exception was raised.
            self.assertEqual([{"a": 1}], merged["tasks"])

    def test_new_payload_without_tasks_key_does_not_crash(self):
        with TemporaryDirectory() as tmp:
            existing = {"model_name": "m", "tasks": [{"a": 1}]}
            path = os.path.join(tmp, "out.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(existing, f)

            new_payload = {"model_name": "m"}  # no tasks
            self.evaluator.save_object(tmp, new_payload, "out.json")

            with open(path, encoding="utf-8") as f:
                merged = json.load(f)
            self.assertEqual([{"a": 1}], merged["tasks"])
