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


class ExactMatch(Metric):
    def compute(self, predictions: List, references: List, **kwargs) -> Dict:
        # Coerce to string and treat None/missing as empty so a malformed prediction
        # counts as a miss instead of crashing the whole computation.
        score = [
            (str(reference) if reference is not None else "").strip()
            == (str(prediction) if prediction is not None else "").strip()
            for reference, prediction in zip(references, predictions)
        ]
        return {"exact_match": sum(score) / len(score) if score else 0.0}


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
