from src.task.task_factory import Task
from tests.tasks.evaluation.task_test_case import TaskTest


class TaskXNLITest(TaskTest):
    def setUp(self) -> None:
        self.dataset_size = 5010

    def test_given_a_prediction_smaller_than_corpus_when_compute_then_return_expected_result_and_warning(
        self,
    ):
        predictions_list = [1, 1, 1, 1, 1]
        a_predictions = {"predictions": predictions_list}
        task = Task(
            task_name="xnli",
            metric="accuracy",
            ground_truths_column_name="label",
        )

        expected_results = {"accuracy": 0.4}
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
        a_predictions = {"predictions": [1] * self.dataset_size}
        task = Task(
            task_name="xnli",
            metric="accuracy",
            ground_truths_column_name="label",
        )

        expected_results = {"accuracy": 0.333333}
        expected_warning = None

        actual_result, actual_warning = task.compute(predictions=a_predictions)

        self.assertEvalDictEqual(expected_results, actual_result)

        self.assertEqual(expected_warning, actual_warning)

    def test_given_a_prediction_larger_than_ground_truth_raise_error(self):
        a_predictions = {"predictions": [1] * (self.dataset_size + 1)}
        task = Task(
            task_name="xnli",
            metric="accuracy",
            ground_truths_column_name="label",
        )

        self.assertRaises(ValueError, task.compute, predictions=a_predictions)
