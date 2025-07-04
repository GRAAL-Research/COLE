import tempfile
from unittest import TestCase

from lighteval.logging.evaluation_tracker import EvaluationTracker
from lighteval.pipeline import PipelineParameters, ParallelismManager

import src.tasks_custom as tasks_module
from src.backend.evaluation_pipeline import evaluation_submission
from src.backend.model import ZipInferenceModel
from src.backend.submit_tools import convert_custom_dict_to_task_dict, get_tasks_as_str


class EvaluationPipelineSts22Test(TestCase):
    def assertDictIsEmpty(self, dict_to_assert):
        self.assertDictEqual(dict_to_assert, {})

    def setUp(self):
        self.task = "sts22"
        self.max_samples = 5

        perfect_preds = [2.0, 1.0, 3.0, 4.0, 2.0]
        raw_perfect = {f"custom|{self.task}|0|0": perfect_preds}
        self.task_dict_perfect = convert_custom_dict_to_task_dict(raw_perfect)

        imperfect_preds = [3.0, 2.0, 4.0, 1.0, 1.0]
        raw_imperfect = {f"custom|{self.task}|0|0": imperfect_preds}
        self.task_dict_imperfect = convert_custom_dict_to_task_dict(raw_imperfect)

        tmp_dir = tempfile.mkdtemp()
        self.tracker = EvaluationTracker(
            output_dir=tmp_dir + "temp",
            save_details=True,
            push_to_hub=False,
        )
        self.pipeline_parameters = PipelineParameters(
            launcher_type=ParallelismManager.ACCELERATE,
            custom_tasks_directory=tasks_module,
            max_samples=self.max_samples,
        )

        self.expected_perfect_pearson = 1.0
        self.expected_imperfect_pearson = -1.0

    def test_given_perfect_predictions_then_pearson_is_one(self):
        self.assertDictIsEmpty(self.tracker.results.get("results"))

        task_str, _ = get_tasks_as_str(self.task_dict_perfect)
        model = ZipInferenceModel(self.task_dict_perfect)

        evaluation_submission(
            task_str=task_str,
            results_tracker=self.tracker,
            pipeline_parameters=self.pipeline_parameters,
            model=model,
        )

        actual = self.tracker.results.get("results").get("all")
        self.assertIn("pearson", actual)
        self.assertAlmostEqual(
            actual["pearson"], self.expected_perfect_pearson, places=5,
            msg="Perfect predictions should yield Pearson of 1.0"
        )

    def test_given_imperfect_predictions_then_pearson_is_negative_one(self):
        # Reset tracker
        self.tracker.results.clear()
        self.assertDictIsEmpty(self.tracker.results.get("results"))

        task_str, _ = get_tasks_as_str(self.task_dict_imperfect)
        model = ZipInferenceModel(self.task_dict_imperfect)

        evaluation_submission(
            task_str=task_str,
            results_tracker=self.tracker,
            pipeline_parameters=self.pipeline_parameters,
            model=model,
        )

        actual = self.tracker.results.get("results").get("all")
        self.assertIn("pearson", actual)
        self.assertAlmostEqual(
            actual["pearson"], self.expected_imperfect_pearson, places=5,
            msg="Reversed predictions should yield Pearson of -1.0"
        )
