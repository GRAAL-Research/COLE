import re
import string
from collections import Counter
from typing import Dict, List

from cole.metrics.metrics_wrapper import Metric


def normalize_answer(answer: str) -> str:
    """
    Lower text and remove punctuation, articles and extra whitespace.
    Based on the SQUAD official metric: https://huggingface.co/spaces/evaluate-metric/squad
    """

    def remove_articles(text):
        # Articles must be removed BEFORE punctuation, because the elided form
        # "l'" carries its apostrophe; once `remove_punc` strips it, "l'eau" becomes
        # "leau" and can no longer be matched. Order matters in French.
        return re.sub(r"\b(le|la|l'|du|des|aux|un|une)\b", " ", text)

    def white_space_fix(text):
        return " ".join(text.split())

    def remove_punc(text):
        exclude = set(string.punctuation) | {"«", "»", "’", "“", "”"}
        apostrophes = {"'", "’", "‘"}
        # Delete apostrophes (as in the original SQuAD metric), but replace other
        # punctuation with spaces to avoid gluing tokens together (e.g. in math expressions).
        parts = []
        for i, ch in enumerate(text):
            if ch in exclude:
                if ch in apostrophes:
                    continue
                # Keep minus sign if it's followed by a digit (negative number)
                if ch == "-" and i + 1 < len(text) and text[i + 1].isdigit():
                    parts.append(ch)
                # Keep dot if it's between two digits (decimal point)
                elif (
                    ch == "."
                    and i > 0
                    and text[i - 1].isdigit()
                    and i + 1 < len(text)
                    and text[i + 1].isdigit()
                ):
                    parts.append(ch)
                else:
                    parts.append(" ")
            else:
                parts.append(ch)
        return "".join(parts)

    answer = str(answer).lower()
    # Normalize spaces around apostrophes (e.g., "l' eau" or "l 'eau" -> "l'eau")
    answer = re.sub(r"\s*['’‘]\s*", "'", answer)
    return white_space_fix(remove_punc(remove_articles(answer)))


def f1_score(prediction: str, ground_truth: str) -> float:
    prediction_tokens = normalize_answer(prediction).split()
    ground_truth_tokens = normalize_answer(ground_truth).split()
    common = Counter(prediction_tokens) & Counter(ground_truth_tokens)
    num_same = sum(common.values())
    if num_same == 0:
        return 0.0
    precision = 1.0 * num_same / len(prediction_tokens)
    recall = 1.0 * num_same / len(ground_truth_tokens)
    f1 = (2 * precision * recall) / (precision + recall)
    return f1


def exact_match_score(prediction: str, ground_truth: str) -> float:
    return normalize_answer(prediction) == normalize_answer(ground_truth)


def metric_max_over_ground_truths(metric_fn, prediction, ground_truths):
    if not ground_truths:
        # No reference answer available — neither exact match nor F1 can be positive.
        return 0.0
    scores_for_ground_truths = []
    for ground_truth in ground_truths:
        score = metric_fn(prediction, ground_truth)
        scores_for_ground_truths.append(score)
    return max(scores_for_ground_truths)


def compute_score(predictions: List, references: List) -> Dict:
    f1 = exact_match = total = 0
    for prediction, reference in zip(predictions, references):
        total += 1

        ground_truths = reference["text"]
        exact_match += metric_max_over_ground_truths(
            exact_match_score, prediction, ground_truths
        )
        f1 += metric_max_over_ground_truths(f1_score, prediction, ground_truths)

    if total == 0:
        return {"exact_match": 0.0, "f1": 0.0}
    exact_match = 100.0 * exact_match / total
    f1 = 100.0 * f1 / total

    return {"exact_match": exact_match, "f1": f1}


class FQuAD(Metric):
    def compute(self, predictions: List, references: List) -> Dict:
        score = compute_score(predictions=predictions, references=references)
        return score
