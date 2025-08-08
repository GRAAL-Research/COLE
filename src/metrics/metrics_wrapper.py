# pylint: disable=unused-argument

import abc
import logging
from abc import ABC
from typing import List, Dict

from evaluate import load


class Metric(ABC):
    @abc.abstractmethod
    def compute(self, predictions, references) -> Dict:
        pass


class AccuracyWrapper(Metric):
    def __init__(self):
        self._metric = load("accuracy")

    def compute(self, predictions: List, references: List, **kwargs) -> Dict:
        if sum(isinstance(p, str) and len(p.strip()) > 2 for p in predictions):
            # Case where some predictions are longer than two digits (i.e. 10, 11, 1).
            # Thus, we extract the first two characters of the string, strip it and except it to be int.
            logging.warning(
                "Applied normalization of predictions due to potential non int response."
            )

            predictions = [
                p[:2].strip().replace(" ", "") if isinstance(p, str) else p
                for p in predictions
            ]
        return self._metric.compute(predictions=predictions, references=references)


class PearsonCorrelation(Metric):
    def __init__(self):
        self._metric = load("pearsonr")

    def compute(self, predictions: List, references: List) -> Dict:
        if sum([len(prediction.strip()) > 2 for prediction in predictions]) > 0:
            logging.warning(
                "Applied normalization of predictions due to potential non int response."
            )
            # Case where some predictions are longer than two digits (i.e. 10, 11, 1).
            # Thus, we extract the first two characters of the string, strip it and except it to be int.
            predictions = [
                prediction[:2].strip().replace(" ", "") for prediction in predictions
            ]

        return self._metric.compute(
            predictions=predictions, references=references, return_pvalue=False
        )


class F1Score(Metric):
    def __init__(self):
        self._metric = load("f1")

    def compute(self, predictions: List, references: List) -> Dict:
        return self._metric.compute(predictions=predictions, references=references)


class ExactMatch(Metric):
    def compute(self, predictions: List, references: List, **kwargs) -> Dict:
        score = [
            reference == prediction
            for reference, prediction in zip(references, predictions)
        ]
        return {"exact_match": sum(score) / len(score)}
