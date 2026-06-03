import json
import tempfile
from pathlib import Path
from unittest import TestCase

from cole.metrics.mixed_questions import (
    evaluate,
    format_report,
    load_jsonl,
    main,
    score_association,
    score_categorization,
    score_multiple_choice,
    score_ordering,
    score_short_answer,
    score_single_choice,
    set_f1,
    to_int,
    to_int_set,
)


class SetF1Test(TestCase):
    def test_two_empty_sets_agree(self):
        self.assertEqual(1.0, set_f1(set(), set()))

    def test_one_empty_set_scores_zero(self):
        self.assertEqual(0.0, set_f1({1}, set()))

    def test_partial_overlap(self):
        # {1, 2} vs {2, 3}: 1 common, precision = recall = 1/2 -> F1 = 0.5.
        self.assertEqual(0.5, set_f1({1, 2}, {2, 3}))


class IntCoercionTest(TestCase):
    def test_to_int_parses_and_folds_invalid(self):
        self.assertEqual(3, to_int("3"))
        self.assertEqual(1, to_int(True))
        self.assertEqual(-1, to_int("abc"))
        self.assertEqual(-1, to_int(None))

    def test_to_int_set_drops_invalid_values(self):
        self.assertEqual({0, 2}, to_int_set([0, "2", "bad"]))
        self.assertEqual(set(), to_int_set(None))
        # A single scalar is accepted as a one-element iterable.
        self.assertEqual({4}, to_int_set(4))


class SingleChoiceTest(TestCase):
    def test_correct_and_incorrect_index(self):
        example = {"question_type": "single_choice", "answer_index": 2}
        self.assertEqual(1.0, score_single_choice(example, 2)["score"])
        # Predictions given as strings are coerced.
        self.assertEqual(1.0, score_single_choice(example, "2")["score"])
        self.assertEqual(0.0, score_single_choice(example, 0)["score"])

    def test_missing_or_none_prediction_scores_zero(self):
        example = {"question_type": "single_choice", "answer_index": 1}
        self.assertEqual(0.0, score_single_choice(example, None)["score"])


class MultipleChoiceTest(TestCase):
    def test_exact_and_partial_credit(self):
        example = {"question_type": "multiple_choice", "answer_indices": [0, 1, 2]}
        perfect = score_multiple_choice(example, [0, 1, 2])
        self.assertEqual(1.0, perfect["score"])
        self.assertEqual(1.0, perfect["exact_match"])
        # {0, 1} vs {0, 1, 2}: precision 1.0, recall 2/3 -> F1 = 0.8.
        partial = score_multiple_choice(example, [0, 1])
        self.assertAlmostEqual(0.8, partial["score"])
        self.assertEqual(0.0, partial["exact_match"])


class ShortAnswerTest(TestCase):
    def test_exact_match_over_accepted_answers(self):
        example = {
            "question_type": "short_answer",
            "answers": ["la photosynthese", "photosynthese"],
        }
        result = score_short_answer(example, "Photosynthese")
        self.assertEqual(1.0, result["exact_match"])
        self.assertEqual(1.0, result["f1"])
        self.assertEqual(1.0, result["score"])

    def test_partial_token_overlap(self):
        example = {"question_type": "short_answer", "answers": ["photosynthese"]}
        # "la" removed -> [grande, photosynthese, verte] vs [photosynthese]:
        # 1 common, precision 1/3, recall 1 -> F1 = 0.5; EM = 0; score = 0.25.
        result = score_short_answer(example, "la grande photosynthese verte")
        self.assertEqual(0.0, result["exact_match"])
        self.assertAlmostEqual(0.5, result["f1"])
        self.assertAlmostEqual(0.25, result["score"])


class AssociationTest(TestCase):
    def test_exact_and_partial_pairs(self):
        example = {
            "question_type": "association",
            "pairs": [
                {"left_index": 0, "right_index": 1},
                {"left_index": 1, "right_index": 0},
            ],
        }
        # Predictions accepted as dicts or as [left, right] sequences.
        perfect = score_association(
            example, [[0, 1], {"left_index": 1, "right_index": 0}]
        )
        self.assertEqual(1.0, perfect["score"])
        self.assertEqual(1.0, perfect["exact_match"])
        # 1 correct pair, 1 predicted, 2 expected -> F1 = 2/3.
        partial = score_association(example, [[0, 1]])
        self.assertAlmostEqual(2 / 3, partial["score"])

    def test_none_prediction_scores_zero(self):
        example = {
            "question_type": "association",
            "pairs": [{"left_index": 0, "right_index": 1}],
        }
        self.assertEqual(0.0, score_association(example, None)["score"])


class CategorizationTest(TestCase):
    def test_fraction_correctly_classified(self):
        example = {
            "question_type": "categorization",
            "assignments": [
                {"element_index": 0, "category_index": 0},
                {"element_index": 1, "category_index": 1},
                {"element_index": 2, "category_index": 0},
            ],
        }
        pred = [
            {"element_index": 0, "category_index": 0},
            {"element_index": 1, "category_index": 0},
            {"element_index": 2, "category_index": 0},
        ]
        result = score_categorization(example, pred)
        self.assertAlmostEqual(2 / 3, result["score"])
        self.assertEqual(0.0, result["exact_match"])


class OrderingTest(TestCase):
    def test_exact_and_pairwise_concordance(self):
        example = {"question_type": "ordering", "ordered_elements": ["a", "b", "c"]}
        perfect = score_ordering(example, ["a", "b", "c"])
        self.assertEqual(1.0, perfect["exact_match"])
        self.assertEqual(1.0, perfect["pairwise_concordance"])
        self.assertEqual(1.0, perfect["score"])
        # One inversion: pairs (a,b) ok, (a,c) ok, (b,c) inverted -> 2/3.
        partial = score_ordering(example, ["a", "c", "b"])
        self.assertEqual(0.0, partial["exact_match"])
        self.assertAlmostEqual(2 / 3, partial["pairwise_concordance"])


def _mixed_examples():
    return [
        {"question_type": "single_choice", "answer_index": 1, "prediction": 1},
        {"question_type": "single_choice", "answer_index": 0, "prediction": 2},
        {"question_type": "short_answer", "answers": ["paris"], "prediction": "Paris"},
        {
            "question_type": "association",
            "pairs": [{"left_index": 0, "right_index": 0}],
            "prediction": [{"left_index": 0, "right_index": 0}],
        },
    ]


class EvaluateTest(TestCase):
    def test_composites_and_per_type(self):
        report = evaluate(_mixed_examples())
        self.assertEqual(4, report["n_examples"])
        self.assertEqual(4, report["n_scored"])
        # single_choice: 1 right out of 2 -> 0.5; short_answer: 1.0; association: 1.0.
        self.assertAlmostEqual(0.5, report["per_type"]["single_choice"]["score"])
        self.assertAlmostEqual(1.0, report["per_type"]["short_answer"]["score"])
        self.assertAlmostEqual(1.0, report["per_type"]["association"]["score"])
        # Unweighted: mean of the 3 type scores x100.
        self.assertAlmostEqual((0.5 + 1.0 + 1.0) / 3 * 100, report["composite_score"])
        # Weighted: per-instance mean; single_choice weighs 2 instances (0 + 1),
        # short_answer 1 (1.0), association 1 (1.0) -> (0 + 1 + 1 + 1) / 4 * 100.
        self.assertAlmostEqual(3.0 / 4 * 100, report["weighted_composite_score"])

    def test_separate_aligned_predictions(self):
        examples = [
            {"question_type": "single_choice", "answer_index": 1},
            {"question_type": "single_choice", "answer_index": 1},
        ]
        report = evaluate(examples, predictions=[1, 0])
        self.assertAlmostEqual(0.5, report["per_type"]["single_choice"]["score"])

    def test_length_mismatch_raises(self):
        examples = [{"question_type": "single_choice", "answer_index": 1}]
        with self.assertRaises(ValueError):
            evaluate(examples, predictions=[1, 2])

    def test_unsupported_type_excluded_from_composite(self):
        examples = [
            {"question_type": "single_choice", "answer_index": 1, "prediction": 1},
            {"question_type": "unknown_matching", "prediction": "x"},
        ]
        report = evaluate(examples)
        self.assertEqual(1, report["n_scored"])
        self.assertEqual({"unknown_matching": 1}, report["unsupported_types"])
        self.assertAlmostEqual(100.0, report["composite_score"])


class IoAndCliTest(TestCase):
    def test_load_jsonl_ignores_blank_lines(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "data.jsonl"
            path.write_text('{"a": 1}\n\n{"b": 2}\n', encoding="utf-8")
            self.assertEqual([{"a": 1}, {"b": 2}], load_jsonl(path))

    def test_main_writes_json_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            gold = Path(tmp) / "gold.jsonl"
            gold.write_text(
                "\n".join(json.dumps(example) for example in _mixed_examples()),
                encoding="utf-8",
            )
            output = Path(tmp) / "report.json"
            report = main([str(gold), "--output", str(output)])
            written = json.loads(output.read_text(encoding="utf-8"))
            self.assertAlmostEqual(
                written["composite_score"], report["composite_score"]
            )
            self.assertIn("single_choice", written["per_type"])

    def test_format_report_mentions_both_composites(self):
        rendered = format_report(evaluate(_mixed_examples()))
        self.assertIn("Unweighted composite", rendered)
        self.assertIn("Weighted composite", rendered)
        self.assertIn("single_choice", rendered)
