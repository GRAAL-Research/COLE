from unittest import TestCase

from src.metrics.fquad_metric import (
    compute_score,
    exact_match_score,
    f1_score,
    metric_max_over_ground_truths,
    normalize_answer,
)


class NormalizeAnswerTest(TestCase):
    def test_lowercases_strips_punctuation_and_articles(self):
        # Articles "le/la/l'/du/des/aux/un/une" should be removed.
        self.assertEqual("chat", normalize_answer("Le chat."))
        self.assertEqual("eau", normalize_answer("L'eau"))
        self.assertEqual("maison", normalize_answer("UNE maison !"))

    def test_collapses_repeated_whitespace(self):
        self.assertEqual("a b c", normalize_answer("a   b\tc"))

    def test_coerces_non_string_input(self):
        self.assertEqual("42", normalize_answer(42))


class F1ScoreTest(TestCase):
    def test_identical_answers_score_one(self):
        self.assertEqual(1.0, f1_score("Le chat dort", "le chat dort"))

    def test_disjoint_answers_score_zero(self):
        self.assertEqual(0.0, f1_score("le chat", "le chien"))

    def test_partial_overlap_is_strictly_between_zero_and_one(self):
        score = f1_score("le chat noir dort", "le chat blanc dort")
        self.assertGreater(score, 0.0)
        self.assertLess(score, 1.0)


class ExactMatchScoreTest(TestCase):
    def test_match_is_case_and_punctuation_insensitive(self):
        self.assertTrue(exact_match_score("Bonjour !", "bonjour"))

    def test_mismatch(self):
        self.assertFalse(exact_match_score("oui", "non"))


class MetricMaxOverGroundTruthsTest(TestCase):
    def test_returns_max_score_across_references(self):
        score = metric_max_over_ground_truths(
            f1_score, "le chat", ["le chien", "le chat"]
        )
        self.assertEqual(1.0, score)

    def test_empty_ground_truths_returns_zero_instead_of_crashing(self):
        # Previously raised ValueError("max() arg is an empty sequence") on
        # malformed dataset rows, taking down the whole batch.
        self.assertEqual(0.0, metric_max_over_ground_truths(f1_score, "anything", []))


class ComputeScoreTest(TestCase):
    def test_aggregates_exact_match_and_f1_as_percentages(self):
        result = compute_score(
            predictions=["le chat", "non"],
            references=[{"text": ["le chat"]}, {"text": ["oui"]}],
        )
        # 1 of 2 exact matches -> 50.0
        self.assertEqual(50.0, result["exact_match"])
        # 1 of 2 perfect F1 -> 50.0
        self.assertEqual(50.0, result["f1"])

    def test_no_predictions_returns_zero_zero(self):
        self.assertEqual(
            {"exact_match": 0.0, "f1": 0.0},
            compute_score(predictions=[], references=[]),
        )
