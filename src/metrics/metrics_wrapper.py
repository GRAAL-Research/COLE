# pylint: disable=unused-argument

import abc
import logging
from abc import ABC
from typing import List, Dict

from evaluate import load

from src import NA_VALUE


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
        score = [
            reference == prediction
            for reference, prediction in zip(references, predictions)
        ]
        return {"exact_match": sum(score) / len(score)}


def apply_int_casting(predictions_to_clean: List) -> List:
    for idx, prediction in enumerate(predictions_to_clean):
        if isinstance(prediction, str):
            logging.warning(
                "Applied normalization of predictions due to potential non int response."
            )
            if prediction.strip().isdigit():
                predictions_to_clean[idx] = float(prediction)
            else:
                predictions_to_clean[idx] = NA_VALUE
        elif prediction is None:
            predictions_to_clean[idx] = NA_VALUE
    return predictions_to_clean
