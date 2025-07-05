from src.task.task_factory import Task
from tests.tasks.evaluation.task_test_case import TaskTest


class TaskOpusParcusTest(TaskTest):
    # We need to have two response otherwise correlation fails (nan).
    def setUp(self) -> None:
        self.dataset_size = 2163048

    def test_given_a_prediction_smaller_than_corpus_when_compute_then_return_expected_result_and_warning(
        self,
    ):
        predictions_list = [75, 75, 75, 75, 75, 90, 90, 90, 90, 90]
        a_predictions = {"predictions": predictions_list}
        task = Task(
            task_name="opus_parcus",
            metric="pearson",
            ground_truths_column_name="quality",
        )

        expected_results = {"pearsonr": -0.3592}
        expected_warning = (
            f"Your prediction size is of '{len(predictions_list)}', while the ground truths size is "
            f"of '{self.dataset_size}'. We computed the metric over the first {len(predictions_list)}"
            f" elements."
        )

        actual_result, actual_warning = task.compute(predictions=a_predictions)

        self.assertEvalDictEqual(expected_results, actual_result)

        self.assertEqual(expected_warning, actual_warning)

    def test_given_a_prediction_when_compute_then_return_expected_result_no_warnings(
        self,
    ):
        a_predictions = {
            "predictions": [75] * (self.dataset_size // 2)
            + [90] * (self.dataset_size // 2)
        }
        task = Task(
            task_name="opus_parcus",
            metric="pearson",
            ground_truths_column_name="quality",
        )

        expected_results = {"pearsonr": -0.0013261}
        expected_warning = None

        actual_result, actual_warning = task.compute(predictions=a_predictions)

        self.assertEvalDictEqual(expected_results, actual_result)

        self.assertEqual(expected_warning, actual_warning)

    def test_given_a_prediction_larger_than_ground_truth_raise_error(self):
        a_predictions = {"predictions": [75] * (self.dataset_size + 1)}
        task = Task(
            task_name="opus_parcus",
            metric="pearson",
            ground_truths_column_name="quality",
        )

        self.assertRaises(ValueError, task.compute, predictions=a_predictions)
