from unittest import TestCase

from src import NA_VALUE
from src.metrics.metrics_wrapper import apply_int_casting


class ApplyIntCasting(TestCase):
    def setUp(self):
        self.a_predictions_list_no_str = [1, 2, 0, 1, 2]
        self.a_predictions_list_str = [1, 2, 0, 1, "2"]
        self.a_prediction_all_str = ["1", "2", "0", "1", "2"]
        self.a_prediction_with_none = [1, 2, 0, 1, 2, None]
        self.a_prediction_string_of_text = ["a", "text", "at", "again", "te"]

    def test_case_no_str(self):
        expected = self.a_predictions_list_no_str

        actual = apply_int_casting(self.a_predictions_list_no_str)

        self.assertEqual(expected, actual)

    def test_case_str(self):
        expected = self.a_predictions_list_no_str

        actual = apply_int_casting(self.a_predictions_list_str)

        self.assertEqual(expected, actual)

    def test_case_all_str(self):
        expected = self.a_predictions_list_no_str

        actual = apply_int_casting(self.a_prediction_all_str)

        self.assertEqual(expected, actual)

    def test_case_with_none(self):
        expected = [1, 2, 0, 1, 2, -1]

        actual = apply_int_casting(self.a_prediction_with_none)

        self.assertEqual(expected, actual)

    def test_case_string_of_text(self):
        expected = [NA_VALUE, NA_VALUE, NA_VALUE, NA_VALUE, NA_VALUE]

        actual = apply_int_casting(self.a_prediction_string_of_text)

        self.assertEqual(expected, actual)
