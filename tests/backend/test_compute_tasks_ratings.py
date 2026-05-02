"""Unit tests for `compute_tasks_ratings` that do not require HF dataset access.

The full integration test in `test_evaluation.py` exercises real datasets and is
gated on HF_TOKEN; this file focuses on the dictionary plumbing (predictions key
handling, deepcopy, response shape) using a stub task.
"""

from typing import Dict, List, Tuple
from unittest import TestCase

from src.backend.evaluation import compute_tasks_ratings


class _StubTask:
    """Duck-typed Task that returns a deterministic score without touching HF."""

    def __init__(self, task_name: str, metric_name: str):
        self.task_name = task_name
        self._metric_name = metric_name

    @property
    def metric_name(self) -> str:
        return self._metric_name

    def compute(self, predictions: List) -> Tuple[Dict, str]:
        return {self._metric_name: float(len(predictions))}, None


class ComputeTasksRatingsKeyHandlingTest(TestCase):
    def test_handles_singular_prediction_key(self):
        # `validate_submission_json` accepts both "prediction" and "predictions".
        # Previously, `compute_tasks_ratings` only popped the plural form and crashed
        # on the singular one, leaking a 500 to the user instead of returning a result.
        tasks = [_StubTask("allocine", "accuracy")]
        submission = {
            "model_name": "m",
            "model_url": "u",
            "tasks": [{"allocine": {"prediction": [1, 1, 1]}}],
        }

        response = compute_tasks_ratings(tasks=tasks, submission=submission)

        self.assertEqual("m", response["model_name"])
        self.assertEqual(
            [{"allocine": {"accuracy": {"accuracy": 3.0, "accuracy_warning": None}}}],
            response["tasks"],
        )

    def test_handles_plural_predictions_key(self):
        tasks = [_StubTask("allocine", "accuracy")]
        submission = {
            "model_name": "m",
            "model_url": "u",
            "tasks": [{"allocine": {"predictions": [1, 0]}}],
        }

        response = compute_tasks_ratings(tasks=tasks, submission=submission)

        self.assertEqual(
            [{"allocine": {"accuracy": {"accuracy": 2.0, "accuracy_warning": None}}}],
            response["tasks"],
        )

    def test_does_not_mutate_caller_submission(self):
        tasks = [_StubTask("allocine", "accuracy")]
        submission = {
            "model_name": "m",
            "model_url": "u",
            "tasks": [{"allocine": {"predictions": [1, 0, 1]}}],
        }
        snapshot_predictions = list(submission["tasks"][0]["allocine"]["predictions"])

        compute_tasks_ratings(tasks=tasks, submission=submission)

        # The deepcopy at the top of compute_tasks_ratings must protect the caller.
        self.assertIn("predictions", submission["tasks"][0]["allocine"])
        self.assertEqual(
            snapshot_predictions, submission["tasks"][0]["allocine"]["predictions"]
        )
