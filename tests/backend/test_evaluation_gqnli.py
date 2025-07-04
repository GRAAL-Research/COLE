import tempfile
from unittest import TestCase

from lighteval.logging.evaluation_tracker import EvaluationTracker
from lighteval.pipeline import PipelineParameters, ParallelismManager

import src.tasks_custom as tasks_module
from src.backend.evaluation_pipeline import evaluation_submission
from src.backend.model import ZipInferenceModel
from src.backend.submit_tools import convert_custom_dict_to_task_dict, get_tasks_as_str

class EValuationPipelineGQNLITest(TestCase):
    def assertDictIsEmpty(self, dict_to_assert):
        self.assertDictEqual(dict_to_assert, {})

    def setUp(self):
        self.a_task = "gqnli"
        self.a_prediction_perfect_score = [1, 2, 1, 0, 1]
        max_samples = 5
        self.a_prediction_perfect_score = {
            f"custom|{self.a_task}|0|0": self.a_prediction_perfect_score
        }

        self.a_prediction_imperfect_score = [0, 0, 0, 1, 0]
        self.a_prediction_imperfect_score = {
            f"custom|{self.a_task}|0|0": self.a_prediction_perfect_score
        }

        self.a_tasks_prediction_dictionary_perfect_score = (
            convert_custom_dict_to_task_dict(self.a_prediction_perfect_score)
        )

        self.a_tasks_prediction_dictionary_imperfect_score = (
            convert_custom_dict_to_task_dict(self.a_prediction_imperfect_score)
        )


        self.task_str, _ = get_tasks_as_str(
            tasks_prediction_dictionary=self.a_tasks_prediction_dictionary_perfect_score
        )

        test_temp_dir = tempfile.mkdtemp()
        test_temp_output_dir = test_temp_dir + "temp"

        self.test_tracker = EvaluationTracker(
            output_dir=test_temp_output_dir, save_details=True, push_to_hub=False
        )

        self.pipeline_parameters = PipelineParameters(
            launcher_type=ParallelismManager.ACCELERATE,
            custom_tasks_directory=tasks_module,
            max_samples=max_samples,
        )

        self.perfect_accuracy_score = 1.0
        self.perfect_acc_stder_score = 0.0

        self.imperfect_accuracy_score = 0
        self.imperfect_acc_stder_score = 0.0

    def test_given_a_perfect_submission_when_evaluate_then_results_is_perfect_score(
        self,
    ):
        # Medium size test since we depend on HG Hub (and Internet) for dataset download.

        self.assertDictIsEmpty(self.test_tracker.results.get("results"))

        expected_results = {"acc": self.perfect_accuracy_score}
        model = ZipInferenceModel(self.a_tasks_prediction_dictionary_perfect_score)

        evaluation_submission(
            task_str=self.task_str,
            results_tracker=self.test_tracker,
            pipeline_parameters=self.pipeline_parameters,
            model=model,
        )

        actual_results = self.test_tracker.results.get("results").get("all")
        self.assertDictEqual(expected_results, actual_results)

    def test_given_a_imperfect_submission_when_evaluate_then_results_is_imperfect_score(
        self,
    ):
        # Medium size test since we depend on HG Hub (and Internet) for dataset download.

        self.assertDictIsEmpty(self.test_tracker.results.get("results"))

        expected_results = {"acc": self.perfect_accuracy_score}
        model = ZipInferenceModel(self.a_tasks_prediction_dictionary_perfect_score)

        evaluation_submission(
            task_str=self.task_str,
            results_tracker=self.test_tracker,
            pipeline_parameters=self.pipeline_parameters,
            model=model,
        )

        actual_results = self.test_tracker.results.get("results").get("all")
        self.assertDictEqual(expected_results, actual_results)
