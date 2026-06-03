"""Evaluator for mixed-type question files (e.g. the Netquiz / COLE corpus).

A single JSONL file can mix several question types (``single_choice``,
``short_answer``, ``association``, ...), each keeping its original type in the
``question_type`` field. A single metric does not fit such a file: the metric
must be chosen per row, based on the question type. This module dispatches each
row to the appropriate COLE metric and aggregates the results.

It reuses COLE's existing metric primitives (``normalize_answer``, ``f1_score``,
``exact_match_score``, ``metric_max_over_ground_truths``) so there is a single
source of truth for text normalisation and FQuAD-style scoring. It only adds the
set-based and structured-question metrics that COLE did not already have
(multiple-choice, association, categorization, ordering).

Two metric families from COLE are used, all in ``[0, 1]``: Accuracy, Exact Match
(normalised, SQuAD-style) and F1 (overlap, partial credit). For a type with
multiple main metrics (``short_answer``, FQuAD-style) the metrics are averaged
into a single type score, following COLE's convention. Two composite scores are
reported: an unweighted mean of the per-type scores (GLUE/COLE style) and a mean
weighted by the number of instances of each type (micro-average over the corpus).

Run from the command line, e.g.::

    python -m cole.metrics.mixed_questions gold.jsonl
    python -m cole.metrics.mixed_questions gold.jsonl --predictions preds.jsonl
"""

import argparse
import json
import logging
from collections.abc import Iterable, Sequence
from itertools import combinations
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from cole import NA_VALUE
from cole.metrics.fquad_metric import (
    exact_match_score,
    f1_score,
    metric_max_over_ground_truths,
)

logger = logging.getLogger(__name__)

# Scale of the composite score (GLUE/COLE style: a percentage in [0, 100]).
COMPOSITE_SCALE = 100.0
# An association pair or a categorization assignment given as a sequence has two members.
PAIR_LENGTH = 2

# Question types, aligned with the Netquiz builder folder names.
SINGLE_CHOICE = "single_choice"
TRUE_FALSE = "true_false"
MULTIPLE_CHOICE = "multiple_choice"
SHORT_ANSWER = "short_answer"
ASSOCIATION = "association"
CATEGORIZATION = "categorization"
ORDERING = "ordering"


def set_f1(predicted: Set[Any], gold: Set[Any]) -> float:
    """F1 over two sets: partial credit for the overlap between them.

    Returns 1.0 when both sets are empty (trivial agreement) and 0.0 when only
    one of them is empty.
    """
    if not predicted and not gold:
        return 1.0
    true_positive = len(predicted & gold)
    if true_positive == 0:
        return 0.0
    precision = true_positive / len(predicted)
    recall = true_positive / len(gold)
    return (2 * precision * recall) / (precision + recall)


def to_int(value: object) -> int:
    """Coerce a value to an int, folding invalid values onto ``NA_VALUE``."""
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError:
            return NA_VALUE
    return NA_VALUE


def to_int_set(values: object) -> Set[int]:
    """Coerce an iterable of values to a set of ints (invalid values dropped)."""
    if values is None:
        return set()
    if isinstance(values, (str, bytes)) or not isinstance(values, Iterable):
        items: Iterable[object] = [values]
    else:
        items = values
    return {
        coerced for coerced in (to_int(item) for item in items) if coerced != NA_VALUE
    }


def _pair_to_tuple(pair: object) -> Optional[Tuple[int, int]]:
    """Convert an association pair to a ``(left, right)`` tuple of ints.

    Accepts a dict (``{"left_index", "right_index"}``) or a two-element sequence.
    Returns ``None`` when the pair is malformed.
    """
    if isinstance(pair, dict):
        left, right = pair.get("left_index"), pair.get("right_index")
    elif (
        isinstance(pair, Sequence)
        and not isinstance(pair, (str, bytes))
        and len(pair) == PAIR_LENGTH
    ):
        left, right = pair[0], pair[1]
    else:
        return None
    left_int, right_int = to_int(left), to_int(right)
    if NA_VALUE in {left_int, right_int}:
        return None
    return (left_int, right_int)


def _pairs_to_set(pairs: object) -> Set[Tuple[int, int]]:
    """Convert a list of association pairs to a set of valid ``(left, right)`` tuples."""
    if not isinstance(pairs, Iterable) or isinstance(pairs, (str, bytes)):
        return set()
    return {tup for tup in (_pair_to_tuple(pair) for pair in pairs) if tup is not None}


def _assignments_to_map(assignments: object) -> Dict[int, int]:
    """Convert categorization assignments to an ``element -> category`` mapping.

    Accepts dicts (``{"element_index", "category_index"}``) or two-element
    sequences ``[element, category]``.
    """
    mapping: Dict[int, int] = {}
    if not isinstance(assignments, Iterable) or isinstance(assignments, (str, bytes)):
        return mapping
    for assignment in assignments:
        if isinstance(assignment, dict):
            element = assignment.get("element_index")
            category = assignment.get("category_index")
        elif (
            isinstance(assignment, Sequence)
            and not isinstance(assignment, (str, bytes))
            and len(assignment) == PAIR_LENGTH
        ):
            element, category = assignment[0], assignment[1]
        else:
            continue
        element_int, category_int = to_int(element), to_int(category)
        if NA_VALUE not in {element_int, category_int}:
            mapping[element_int] = category_int
    return mapping


def score_single_choice(
    example: Dict[str, Any], prediction: object
) -> Dict[str, float]:
    """Score a single-choice (or true/false) question: accuracy on the chosen index."""
    gold = to_int(example.get("answer_index"))
    accuracy = float(gold != NA_VALUE and to_int(prediction) == gold)
    return {"accuracy": accuracy, "score": accuracy}


def score_multiple_choice(
    example: Dict[str, Any], prediction: object
) -> Dict[str, float]:
    """Score a multiple-choice question: set F1 (partial credit) plus exact set match."""
    gold = to_int_set(example.get("answer_indices"))
    predicted = to_int_set(prediction)
    f1 = set_f1(predicted, gold)
    exact = float(predicted == gold)
    return {"f1": f1, "exact_match": exact, "score": f1}


def score_short_answer(example: Dict[str, Any], prediction: object) -> Dict[str, float]:
    """Score a short-answer question: FQuAD-style EM and F1, max over accepted answers.

    The ground truth is the ``answers`` list of accepted answers. The primary
    score is the mean of EM and F1, following COLE's convention for tasks with
    multiple main metrics.
    """
    ground_truths = example.get("answers")
    if not isinstance(ground_truths, Sequence) or isinstance(
        ground_truths, (str, bytes)
    ):
        ground_truths = [ground_truths] if ground_truths is not None else []
    exact = float(
        metric_max_over_ground_truths(exact_match_score, prediction, ground_truths)
    )
    f1 = metric_max_over_ground_truths(f1_score, prediction, ground_truths)
    return {"exact_match": exact, "f1": f1, "score": (exact + f1) / 2}


def score_association(example: Dict[str, Any], prediction: object) -> Dict[str, float]:
    """Score an association question: F1 over the set of correct pairs plus exact match."""
    gold = _pairs_to_set(example.get("pairs"))
    predicted = _pairs_to_set(prediction)
    f1 = set_f1(predicted, gold)
    exact = float(predicted == gold)
    return {"f1": f1, "exact_match": exact, "score": f1}


def score_categorization(
    example: Dict[str, Any], prediction: object
) -> Dict[str, float]:
    """Score a categorization question: fraction of correctly classified elements plus EM."""
    gold = _assignments_to_map(example.get("assignments"))
    predicted = _assignments_to_map(prediction)
    if not gold:
        accuracy = 0.0
    else:
        correct = sum(
            1
            for element, category in gold.items()
            if predicted.get(element) == category
        )
        accuracy = correct / len(gold)
    exact = float(predicted == gold)
    return {"accuracy": accuracy, "exact_match": exact, "score": accuracy}


def score_ordering(example: Dict[str, Any], prediction: object) -> Dict[str, float]:
    """Score an ordering question: strict EM plus pairwise concordance.

    The ground truth ``ordered_elements`` is the correct order. EM requires the
    exact order; the pairwise concordance (Kendall-style, normalised to ``[0, 1]``)
    gives partial credit based on the fraction of element pairs ordered correctly.
    The primary score is the EM, faithful to COLE's strict use of EM for
    generative tasks.
    """
    gold = example.get("ordered_elements")
    gold_list = (
        list(gold) if isinstance(gold, Sequence) and not isinstance(gold, str) else []
    )
    pred_list = (
        list(prediction)
        if isinstance(prediction, Sequence) and not isinstance(prediction, str)
        else []
    )
    exact = float(pred_list == gold_list and len(gold_list) > 0)

    rank = {element: position for position, element in enumerate(pred_list)}
    concordant = 0
    total = 0
    for left, right in combinations(gold_list, 2):
        total += 1
        if left in rank and right in rank and rank[left] < rank[right]:
            concordant += 1
    pairwise = (concordant / total) if total else exact
    return {"exact_match": exact, "pairwise_concordance": pairwise, "score": exact}


# Dispatch registry: question type -> scorer. ``true_false`` shares the single-choice
# scorer (binary classification on a single index).
SCORERS: Dict[str, Callable[[Dict[str, Any], object], Dict[str, float]]] = {
    SINGLE_CHOICE: score_single_choice,
    TRUE_FALSE: score_single_choice,
    MULTIPLE_CHOICE: score_multiple_choice,
    SHORT_ANSWER: score_short_answer,
    ASSOCIATION: score_association,
    CATEGORIZATION: score_categorization,
    ORDERING: score_ordering,
}


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    """Load a JSONL file into a list of dicts (blank lines ignored)."""
    rows: List[Dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                rows.append(json.loads(stripped))
    return rows


def _aggregate_type(metrics: List[Dict[str, float]]) -> Dict[str, Any]:
    """Aggregate the per-example metrics of one type into their means."""
    count = len(metrics)
    keys = {key for metric in metrics for key in metric}
    averaged: Dict[str, Any] = {
        key: sum(metric.get(key, 0.0) for metric in metrics) / count for key in keys
    }
    averaged["count"] = count
    return averaged


def evaluate(
    examples: Sequence[Dict[str, Any]],
    predictions: Optional[Sequence[object]] = None,
    prediction_key: str = "prediction",
) -> Dict[str, Any]:
    """Evaluate mixed-type questions, choosing the metric per question type.

    Each example is routed, based on its ``question_type`` field, to the matching
    scorer. Scores are aggregated per type, then combined into two composite
    scores: an unweighted mean of the per-type scores (GLUE/COLE style) and a mean
    weighted by the number of instances of each type (micro-average).

    Args:
        examples: Annotated examples (ground truth), each with a ``question_type``.
        predictions: Predictions aligned by position with ``examples``. When
            ``None``, each example's prediction is read from ``prediction_key``.
        prediction_key: Field holding the prediction when ``predictions`` is None.

    Returns:
        A structured report: both composite scores, per-type scores and mean
        metrics, counts, and the list of unsupported types encountered.

    Raises:
        ValueError: If ``predictions`` is given but its length differs from
            ``examples``.
    """
    if predictions is not None and len(predictions) != len(examples):
        raise ValueError(
            f"Number of predictions ({len(predictions)}) differs from the number "
            f"of examples ({len(examples)})."
        )

    per_type_metrics: Dict[str, List[Dict[str, float]]] = {}
    unsupported: Dict[str, int] = {}

    for index, example in enumerate(examples):
        question_type = str(example.get("question_type", "")).strip()
        scorer = SCORERS.get(question_type)
        if scorer is None:
            key = question_type or "<missing>"
            unsupported[key] = unsupported.get(key, 0) + 1
            continue
        prediction = (
            predictions[index]
            if predictions is not None
            else example.get(prediction_key)
        )
        per_type_metrics.setdefault(question_type, []).append(
            scorer(example, prediction)
        )

    per_type_report = {
        question_type: _aggregate_type(metrics)
        for question_type, metrics in per_type_metrics.items()
    }
    type_scores = [report["score"] for report in per_type_report.values()]
    composite = (
        (sum(type_scores) / len(type_scores) * COMPOSITE_SCALE) if type_scores else 0.0
    )

    # Weighted composite: each type contributes in proportion to its instance count,
    # i.e. the mean of the per-instance scores over the whole corpus.
    n_scored = sum(report["count"] for report in per_type_report.values())
    weighted_sum = sum(
        report["score"] * report["count"] for report in per_type_report.values()
    )
    weighted_composite = (
        (weighted_sum / n_scored * COMPOSITE_SCALE) if n_scored else 0.0
    )

    if unsupported:
        logger.warning(
            "Unsupported question types ignored (excluded from the composite scores): %s",
            unsupported,
        )

    return {
        "composite_score": composite,
        "weighted_composite_score": weighted_composite,
        "n_examples": len(examples),
        "n_scored": n_scored,
        "per_type": per_type_report,
        "unsupported_types": unsupported,
    }


def format_report(report: Dict[str, Any]) -> str:
    """Format an evaluation report into human-readable text."""
    lines = [
        "=== Mixed-type question evaluation ===",
        f"Examples: {report['n_examples']} | scored: {report['n_scored']}",
        f"Unweighted composite (mean of types x100): {report['composite_score']:.2f}",
        f"Weighted composite (by instance count x100): {report['weighted_composite_score']:.2f}",
        "",
        "Per question type:",
    ]
    for question_type in sorted(report["per_type"]):
        stats = report["per_type"][question_type]
        detail = ", ".join(
            f"{key}={value:.4f}"
            for key, value in sorted(stats.items())
            if key not in {"count", "score"}
        )
        suffix = f"  [{detail}]" if detail else ""
        lines.append(
            f"  - {question_type:<16} n={stats['count']:<5} score={stats['score']:.4f}{suffix}"
        )
    if report["unsupported_types"]:
        lines.extend(
            ["", f"Unsupported types (ignored): {report['unsupported_types']}"]
        )
    return "\n".join(lines)


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate a mixed-type question JSONL file, choosing the metric per "
            "question type (COLE logic)."
        ),
    )
    parser.add_argument("gold", type=Path, help="Annotated JSONL file (ground truth).")
    parser.add_argument(
        "--predictions",
        type=Path,
        default=None,
        help=(
            "JSONL predictions file aligned line by line with the gold file. When "
            "omitted, the prediction is read from each line's --prediction-key field."
        ),
    )
    parser.add_argument(
        "--prediction-key",
        default="prediction",
        help="Field holding the prediction when --predictions is omitted.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Path to write the JSON report to (in addition to the text output).",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> Dict[str, Any]:
    """CLI entry point: evaluate an annotated file and print the report."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args(argv)
    examples = load_jsonl(args.gold)
    predictions: Optional[List[object]] = None
    if args.predictions is not None:
        predictions = [
            row.get(args.prediction_key) for row in load_jsonl(args.predictions)
        ]
    report = evaluate(
        examples, predictions=predictions, prediction_key=args.prediction_key
    )
    print(format_report(report))
    if args.output is not None:
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"\nJSON report written to {args.output}")
    return report


if __name__ == "__main__":
    main()
