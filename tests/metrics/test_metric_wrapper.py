from unittest import TestCase

from cole import NA_VALUE
from cole.metrics.metrics_wrapper import ExactMatch, apply_int_casting


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

    def test_does_not_mutate_caller_list(self):
        # Previously the function modified the input in-place, which silently
        # corrupted the upstream submission payload that owned the list.
        original = ["1", "2", None, "x"]
        snapshot = list(original)

        cleaned = apply_int_casting(original)

        self.assertEqual(snapshot, original)
        self.assertEqual([1, 2, NA_VALUE, NA_VALUE], cleaned)
        self.assertIsNot(original, cleaned)

    def test_bool_is_normalized_to_int(self):
        # Without the explicit bool branch, True/False would pass the `isinstance(int)`
        # check unchanged and reach the metric backend as boolean values.
        actual = apply_int_casting([True, False, True])
        self.assertEqual([1, 0, 1], actual)
        # `type(v) is int` is intentional: `isinstance(v, int)` would accept bool
        # because bool is a subclass of int, defeating the purpose of this check.
        self.assertTrue(
            all(type(v) is int for v in actual)  # pylint: disable=unidiomatic-typecheck
        )


class ExactMatchComputeTest(TestCase):
    def setUp(self):
        self.metric = ExactMatch()

    def test_returns_zero_when_inputs_are_empty(self):
        self.assertEqual({"exact_match": 0.0}, self.metric.compute([], []))

    def test_perfect_match_returns_one(self):
        self.assertEqual(
            {"exact_match": 1.0},
            self.metric.compute(["a", " b "], ["a ", "b"]),
        )

    def test_none_prediction_does_not_crash(self):
        # Previously raised AttributeError on `prediction.strip()` when the model
        # returned None for a row.
        # Behaviour change: failed (None) predictions are now excluded from the denominator
        # and reported in `na_count` instead of silently counting as misses.
        result = self.metric.compute(
            ["valid", None], ["valid", "valid"], max_na_fraction=0.5
        )
        self.assertEqual({"exact_match": 1.0, "na_count": 1}, result)

    def test_na_heavy_predictions_raise(self):
        with self.assertRaises(ValueError):
            self.metric.compute(["NA", "NA", "NA", "a"], ["a"] * 4)

    def test_few_na_excluded_and_reported(self):
        result = self.metric.compute(["NA"] + ["a"] * 9, ["a"] * 10)
        self.assertEqual({"exact_match": 1.0, "na_count": 1}, result)

    def test_non_string_prediction_is_coerced(self):
        result = self.metric.compute([42, "answer"], ["42", "answer"])
        self.assertEqual({"exact_match": 1.0}, result)
