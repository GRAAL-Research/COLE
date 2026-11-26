# pylint: disable=unused-argument

import abc
import logging
from abc import ABC
from typing import List, Dict

from evaluate import load

from cole import NA_VALUE


class Metric(ABC):
    @abc.abstractmethod
    def compute(self, predictions, references) -> Dict:
        pass


class AccuracyWrapper(Metric):
    def __init__(self):
        self._metric = load("accuracy")

    def compute(self, predictions: List, references: List, **kwargs) -> Dict:
        clean_predictions = apply_int_casting(predictions_to_clean=predictions)
        return self._metric.compute(
            predictions=clean_predictions, references=references
        )


class PearsonCorrelation(Metric):
    def __init__(self):
        self._metric = load("pearsonr")

    def compute(self, predictions: List, references: List) -> Dict:
        clean_predictions = apply_int_casting(predictions_to_clean=predictions)
        return self._metric.compute(
            predictions=clean_predictions, references=references, return_pvalue=False
        )


class F1Score(Metric):
    def __init__(self):
        self._metric = load("f1")

    def compute(self, predictions: List, references: List) -> Dict:
        clean_predictions = apply_int_casting(predictions_to_clean=predictions)
        return self._metric.compute(
            predictions=clean_predictions, references=references
        )


DEFAULT_MAX_NA_FRACTION = 0.2
_FAILED_MARKERS = {"", "NA", str(NA_VALUE)}


def is_failed_prediction(prediction) -> bool:
    """True when the prediction is a pipeline failure marker (None, empty, "NA" or "-1")."""
    if prediction is None:
        return True
    return str(prediction).strip() in _FAILED_MARKERS


def guard_failed_predictions(
    failed: int, total: int, max_na_fraction: float = DEFAULT_MAX_NA_FRACTION
) -> None:
    """Raise when too many predictions failed, so a pipeline failure can not look like a 0.0 score."""
    if total > 0 and failed / total > max_na_fraction:
        raise ValueError(
            f"{failed} of {total} predictions are failed/NA "
            f"(> {max_na_fraction:.0%}); the evaluation pipeline likely failed, "
            "refusing to report a score."
        )


class ExactMatch(Metric):
    def compute(
        self,
        predictions: List,
        references: List,
        max_na_fraction: float = DEFAULT_MAX_NA_FRACTION,
        **kwargs,
    ) -> Dict:
        pairs = list(zip(references, predictions))
        failed = sum(is_failed_prediction(prediction) for _, prediction in pairs)
        guard_failed_predictions(failed, len(pairs), max_na_fraction)
        # Failed predictions are excluded from the denominator and reported in `na_count`.
        score = [
            (str(reference) if reference is not None else "").strip()
            == str(prediction).strip()
            for reference, prediction in pairs
            if not is_failed_prediction(prediction)
        ]
        result = {"exact_match": sum(score) / len(score) if score else 0.0}
        if failed:
            result["na_count"] = failed
        return result


def apply_int_casting(predictions_to_clean: List) -> List:
    # Operate on a copy to avoid mutating the caller's list (e.g. the submission payload).
    cleaned = list(predictions_to_clean)
    na_value = 0
    none_value = 0
    undetected_value = 0
    for idx, prediction in enumerate(cleaned):
        if isinstance(prediction, bool):
            # bool is a subclass of int; cast to int explicitly to avoid True/False leaking through.
            cleaned[idx] = int(prediction)
        elif isinstance(prediction, int):
            # Case where the prediction is already an int.
            # We use this branch since we want an else statement to capture undetected type.
            pass
        elif isinstance(prediction, float):
            cleaned[idx] = int(prediction)
        elif isinstance(prediction, str):
            try:
                cleaned[idx] = int(prediction.strip())
            except ValueError:
                na_value += 1
                cleaned[idx] = NA_VALUE
        elif prediction is None:
            none_value += 1
            cleaned[idx] = NA_VALUE
        else:
            undetected_value += 1
            cleaned[idx] = NA_VALUE
    if na_value > 0:
        warning_message = f"Number of na_value during int casting: {na_value}"
        logging.warning(warning_message)
    if none_value > 0:
        warning_message = f"Number of none_value during int casting: {none_value}"
        logging.warning(warning_message)
    if undetected_value > 0:
        warning_message = (
            f"Number of undetected_value during int casting: {undetected_value}"
        )
        logging.warning(warning_message)
    return cleaned
