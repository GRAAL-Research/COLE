from src.task.task import TaskType
from src.task.task_factory import Task
from tests.tasks.evaluation.task_test_case import TaskTest


class Taskwino_x_lmTest(TaskTest):
    def setUp(self) -> None:
        self.dataset_size = 2793

    def test_given_a_prediction_smaller_than_corpus_when_compute_then_return_expected_result_and_warning(
        self,
    ):
        a_predictions = [1, 1, 1, 1, 1]
        task = Task(
            task_name="wino_x_lm",
            metric="accuracy",
            task_type=TaskType.INFERENCE,
        )

        expected_results = {"accuracy": 0.6}
        expected_warning = (
            f"Your prediction size is of '{len(a_predictions)}', while the ground truths size is "
            f"of '{self.dataset_size}'. We computed the metric over the first {len(a_predictions)}"
            f" elements."
        )

        actual_result, actual_warning = task.compute(predictions=a_predictions)

        self.assertEvalDictEqual(expected_results, actual_result)

        self.assertEqual(expected_warning, actual_warning)

    def test_given_a_prediction_when_compute_then_return_expected_result_no_warnings(
        self,
    ):
        a_predictions = [1] * self.dataset_size
        task = Task(
            task_name="wino_x_lm",
            metric="accuracy",
            task_type=TaskType.INFERENCE,
        )

        expected_results = {"accuracy": 0.5}
        expected_warning = None

        actual_result, actual_warning = task.compute(predictions=a_predictions)

        self.assertEvalDictEqual(expected_results, actual_result)

        self.assertEqual(expected_warning, actual_warning)

    def test_given_a_prediction_larger_than_ground_truth_raise_error(self):
        a_predictions = [1] * (self.dataset_size + 1)
        task = Task(
            task_name="wino_x_lm",
            metric="accuracy",
            task_type=TaskType.INFERENCE,
        )

        self.assertRaises(ValueError, task.compute, predictions=a_predictions)
