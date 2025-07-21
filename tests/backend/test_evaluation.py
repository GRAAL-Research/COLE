import copy
from typing import Dict, List
from unittest import TestCase
from unittest.mock import ANY

from src.backend.evaluation import compute_tasks_ratings
from src.task.task_factory import Task


class ComputeTasksRatingsTest(TestCase):
    def setUp(self) -> None:
        a_prediction_list = [1, 1, 1, 1, 1]

        self.a_task_dict = {"predictions": a_prediction_list}

    def create_submission_dict(self, tasks: List[Task]) -> Dict:
        return {task.task_name: self.a_task_dict for task in tasks}

    def create_expected_submission_response(
        self, tasks: List[Task], submission_dict: Dict
    ) -> Dict:
        expected_submission_response = copy.deepcopy(submission_dict)
        for task in tasks:
            expected_submission_response.get(task.task_name).update(
                {f"{task.metric_name}": ANY}
            )
        return expected_submission_response

    def test_evaluation_loop(self):
        tasks = [
            Task(
                task_name="allocine",
                metric="accuracy",
            ),
            Task(
                task_name="fquad",
                metric="fquad",
            ),
        ]

        submission = {
            "model_name": "a_model_name",
            "model_url": "a_model_url",
            "tasks": [
                {"allocine": {"predictions": [1, 1, 1, 1, 1]}},
                {
                    "fquad": {
                        "predictions": [
                            "par un mauvais état de santé",
                            "par un mauvais état de santé",
                            "par un mauvais état de santé",
                            "par un mauvais état de santé",
                            "par un mauvais état de santé",
                        ]
                    }
                },
            ],
        }

        expected_response = {
            "model_name": "a_model_name",
            "model_url": "a_model_url",
            "tasks": [
                {
                    "allocine": {
                        "accuracy": {
                            "accuracy": 0.4,
                            "accuracy_warning": "Your prediction size is of '5', while the "
                            "ground truths size is of '20000'."
                            " We computed the metric over the first 5 elements.",
                        },
                    }
                },
                {
                    "fquad": {
                        "fquad": {
                            "exact_match": 20.0,
                            "f1": 25.33333333332,
                            "fquad_warning": "Your prediction size is of '5', "
                            "while the ground truths size is of '400'. "
                            "We computed the metric over the first 5 elements.",
                        },
                    }
                },
            ],
        }

        actual_response = compute_tasks_ratings(tasks=tasks, submission=submission)

        self.assertEqual(
            expected_response.get("model_name"), actual_response.get("model_name")
        )
        self.assertEqual(
            expected_response.get("model_url"), actual_response.get("model_url")
        )
        self.assertEqual(
            len(expected_response.get("tasks")), len(actual_response.get("tasks"))
        )
        self.assertAlmostEqual(
            expected_response.get("tasks")[0]
            .get("allocine")
            .get("accuracy")
            .get("accuracy"),
            actual_response.get("tasks")[0]
            .get("allocine")
            .get("accuracy")
            .get("accuracy"),
        )
        self.assertAlmostEqual(
            expected_response.get("tasks")[1]
            .get("fquad")
            .get("fquad")
            .get("exact_match"),
            actual_response.get("tasks")[1]
            .get("fquad")
            .get("fquad")
            .get("exact_match"),
        )
        self.assertAlmostEqual(
            expected_response.get("tasks")[1].get("fquad").get("fquad").get("f1"),
            actual_response.get("tasks")[1].get("fquad").get("fquad").get("f1"),
        )
        self.assertEqual(
            None, actual_response.get("tasks")[1].get("fquad").get("predictions")
        )
        self.assertEqual(
            None, actual_response.get("tasks")[0].get("allocine").get("predictions")
        )
