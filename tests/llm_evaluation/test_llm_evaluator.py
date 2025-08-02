# pylint: disable=unused-argument

from typing import List, Dict
from unittest import TestCase, mock

from src.dataset.dataset import Dataset
from src.evaluation.llm_evaluator import ModelEvaluator
from src.language_model.language_model_abstraction import LanguageModel
from src.task.task import Task
from src.task.task_factory import tasks_factory

MODEL_NAME = "a_model"
preds = ["0"] * 7546  # qfrcola dataset size
gen = ["0"] * 7546  # qfrcola dataset size
BASE_TASK_NAME = "qfrcola"


class ForTestModel(LanguageModel):
    def predict(self, evaluation_dataset: Dataset, task: Task):
        return ["0" for _ in range(len(evaluation_dataset))]

    def infer(self, rows: List[str]):
        return ["0" for _ in range(len(rows))]

    def generate(self, rows: List[str]):
        raise NotImplementedError

    def unload_model(self):
        pass


class ModelEvaluatorTest(TestCase):
    def assertEvalDictEqual(self, dict1: Dict, dict2: Dict) -> None:
        for (key_1, value_1), (key_2, value_2) in zip(dict1.items(), dict2.items()):
            self.assertEqual(key_1, key_2)
            self.assertAlmostEqual(value_1, value_2, delta=0.1)

    def setUp(self):
        self.model = ForTestModel(MODEL_NAME)
        self.model.infer = lambda *args, **kwargs: preds
        self.model.generate = lambda *args, **kwargs: gen
        self.tester = ModelEvaluator()
        self.tasks = tasks_factory([BASE_TASK_NAME])

    @mock.patch("src.evaluation.llm_evaluator.wandb")
    def test_when_evaluating_return_formatted_dict(self, wandb_mock):
        ret = self.tester.evaluate(self.model, self.tasks)

        assert ret == {
            "model_name": MODEL_NAME,
            "model_url": "https://huggingface.co/a_model",
            "tasks": [{"qfrcola": preds}],
        }

    @mock.patch("src.evaluation.llm_evaluator.wandb")
    def test_when_compute_metrics_return_metrics_dict(self, wandb_mock):
        self.tester.last_model_name = "test/model"
        self.tester.evaluate(self.model, self.tasks)
        actual_metrics = self.tester.compute_metrics()

        expected = {
            "model_name": MODEL_NAME,
            "model_url": "https://huggingface.co/a_model",
            "tasks": [
                {
                    "qfrcola": {
                        "accuracy": {
                            "accuracy": 0.305,
                            "accuracy_warning": None,
                        }
                    }
                }
            ],
        }
        for key in expected:
            if key == "tasks":
                expected_task_payload = (
                    expected.get(key)[0].get("qfrcola").get("accuracy")
                )
                actual_task_payload = (
                    actual_metrics.get(key)[0].get("qfrcola").get("accuracy")
                )

                self.assertAlmostEqual(
                    expected_task_payload.get("accuracy"),
                    actual_task_payload.get("accuracy"),
                    delta=0.1,
                )
                self.assertEqual(
                    expected_task_payload.get("accuracy_warning"),
                    actual_task_payload.get("accuracy_warning"),
                )
            else:
                self.assertEqual(expected.get(key), actual_metrics.get(key))

    @mock.patch("src.evaluation.llm_evaluator.wandb")
    def test_when_task_is_generative_generate(self, wandb_mock):
        TASK_NAME = "qfrcola"
        tasks = tasks_factory([TASK_NAME])
        predictions = self.tester.evaluate(self.model, tasks)
        assert predictions["tasks"] == [{TASK_NAME: gen}]

    @mock.patch("src.evaluation.llm_evaluator.wandb")
    def test_when_task_is_inference_infer(self, wandb_mock):
        ret = self.tester.evaluate(self.model, self.tasks)
        assert ret["tasks"] == [{BASE_TASK_NAME: preds}]
