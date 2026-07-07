from unittest import TestCase
import sympy as sp

from cole.metrics.math_metric import (
    parse_math_expression,
    math_exact_match_score,
    math_f1_score,
)


class MathMetricTest(TestCase):
    def test_parse_math_expression_numeric(self):
        self.assertEqual(5.0, parse_math_expression("5"))
        self.assertEqual(1.5, parse_math_expression("1.5"))
        self.assertEqual(-3.0, parse_math_expression("-3"))

    def test_parse_math_expression_fractions(self):
        # 1/2 is parsed as a SymPy Rational or Expr
        expr = parse_math_expression("1/2")
        self.assertTrue(isinstance(expr, sp.Basic))
        self.assertEqual(0.5, float(expr))

    def test_parse_math_expression_list_and_coords(self):
        self.assertEqual((24.0, 14.0), parse_math_expression("(24, 14)"))
        self.assertEqual((24.0, 14.0), parse_math_expression("24,14"))
        self.assertEqual((47.0, 53.0), parse_math_expression("47, 53"))

    def test_parse_math_expression_symbols(self):
        # 2^5 should evaluate to 32 (via 2**5 in python/sympy syntax)
        expr = parse_math_expression("2^5")
        self.assertEqual(32, int(expr))

        # 2-5 should evaluate to -3
        expr_sub = parse_math_expression("2-5")
        self.assertEqual(-3, int(expr_sub))

    def test_parse_math_expression_fallback(self):
        self.assertEqual("section a", parse_math_expression("Section A"))

    def test_math_exact_match_score(self):
        # Exponents and spacing
        self.assertTrue(math_exact_match_score("2^5", "2 ^ 5"))
        self.assertTrue(math_exact_match_score("2^5", "32"))

        # Avoid SQuAD/FQuAD collisions
        self.assertFalse(math_exact_match_score("2^5", "2-5"))

        # Decimals & Fractions
        self.assertTrue(math_exact_match_score("1/2", "0.5"))

        # Lists and spaces
        self.assertTrue(math_exact_match_score("(24, 14)", "24,14"))
        self.assertTrue(math_exact_match_score("47, 53", "47,53"))

        # Fallback text matches
        self.assertTrue(math_exact_match_score("Section A", "section a"))
        self.assertFalse(math_exact_match_score("Section A", "Section B"))

        # Long algebraic expressions (expansion, factorization, spacing)
        self.assertTrue(math_exact_match_score("(x - 1)*(2*x + 3)", "2*x**2 + x - 3"))
        self.assertTrue(
            math_exact_match_score("2  *  x  **  2   +   5 * x   -   3", "2*x**2+5*x-3")
        )
        self.assertFalse(math_exact_match_score("2*x**2 + 5*x - 3", "2*x**2 + 5*x - 4"))

    def test_math_f1_score(self):
        self.assertEqual(1.0, math_f1_score("2^5", "2 ^ 5"))
        self.assertEqual(1.0, math_f1_score("(24, 14)", "24,14"))
        self.assertEqual(1.0, math_f1_score("1/2", "0.5"))

        # Long algebraic expression spacing (perfect score)
        self.assertEqual(
            1.0, math_f1_score("2  *  x  **  2   +   5 * x   -   3", "2*x**2+5*x-3")
        )

        # Partial overlap on text/math tokens
        score = math_f1_score("x + y + z", "x + y")
        self.assertGreater(score, 0.0)
        self.assertLess(score, 1.0)

        # Partial credit on long algebraic expression typos
        partial_score = math_f1_score("2*x**2 + 5*x - 4", "2*x**2 + 5*x - 3")
        self.assertAlmostEqual(22 / 24, partial_score)

    def test_numeric_ground_truth_is_coerced(self):
        # Ground truths stored as JSON numbers (common for math answers) must not
        # crash the parser, which strips strings. Regression: raised AttributeError.
        self.assertEqual(42.0, parse_math_expression(42))
        self.assertTrue(math_exact_match_score("42", 42))
        self.assertTrue(math_exact_match_score(3.14, "3.14"))
        self.assertEqual(1.0, math_f1_score(42, "42"))

    def test_identical_answers_are_reflexive(self):
        # Exact-match must be reflexive even when SymPy parses a token to a value
        # that never equals itself (e.g. float NaN).
        self.assertTrue(math_exact_match_score("nan", "nan"))
        self.assertEqual(1.0, math_f1_score("nan", "nan"))
        self.assertTrue(math_exact_match_score("Section A", "section a"))

    def test_french_decimal_comma_matches_dot(self):
        # French decimal notation "3,14" must match "3.14" in a Quebec benchmark.
        self.assertTrue(math_exact_match_score("3,14", "3.14"))
        self.assertTrue(math_exact_match_score("3.14", "3,14"))
        self.assertTrue(math_exact_match_score("-2,5", "-2.5"))
        self.assertEqual(1.0, math_f1_score("3,14", "3.14"))

    def test_coordinates_still_match_as_tuples(self):
        # The decimal reading must not break genuine coordinate/list answers.
        self.assertTrue(math_exact_match_score("(24, 14)", "24,14"))
        self.assertTrue(math_exact_match_score("47, 53", "47,53"))

    def test_distinct_decimals_do_not_match(self):
        # Double interpretation must not create false positives.
        self.assertFalse(math_exact_match_score("3,14", "3,15"))
        self.assertFalse(math_exact_match_score("3,14", "3.15"))
