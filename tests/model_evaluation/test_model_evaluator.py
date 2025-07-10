import json
from unittest import TestCase

from src.evaluation.model_evaluator import ModelEvaluator
from src.model.model import Model
from src.task.task_factory import tasks_factory

MODEL_NAME = "a model"
preds = ["0", "0", "0", "0"]


class ModelEvaluatorTest(TestCase):

    def setUp(self):
        self.model = Model(MODEL_NAME)
        self.model.infer = lambda *args, **kwargs: preds
        self.model.generate = lambda *args, **kwargs: ["0", "0", "0"]
        self.tester = ModelEvaluator()
        self.tasks = tasks_factory(["qfrcola"])

    def test_when_evaluating_return_formatted_dict(self):
        ret = self.tester.evaluate(self.model, self.tasks)

        assert ret == {
            "model_name": MODEL_NAME,
            "model_url": "No URL provided",
            "tasks": [{"qfrcola": preds}],
        }

    def test_when_compute_metrics_return_metrics_dict(self):
        self.tester.last_model_name = "test/model"
        self.tester.evaluate(self.model, self.tasks)
        metrics = self.tester.compute_metrics()
        print(metrics)
        assert metrics == {
            "model_name": MODEL_NAME,
            "model_url": "No URL provided",
            "tasks": [
                {
                    "qfrcola": {
                        "accuracy": {
                            "accuracy": 0.5,
                            f"accuracy_warning": f"Your prediction size is of {len(preds)}, while the ground truths size is of {len(self.tasks[0].dataset.ground_truths)}. We computed the metric over the first {len(preds)} elements.",
                        }
                    }
                }
            ],
        }
