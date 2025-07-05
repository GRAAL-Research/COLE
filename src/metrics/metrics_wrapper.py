# pylint: disable=unused-argument

import abc
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
        return self._metric.compute(predictions=predictions, references=references)


class PearsonCorrelation(Metric):
    def __init__(self):
        self._metric = load("pearsonr")

    def compute(self, predictions: List, references: List) -> Dict:
        return self._metric.compute(
            predictions=predictions, references=references, return_pvalue=False
        )


class F1Score(Metric):
    def __init__(self):
        self._metric = load("f1")

    def compute(self, predictions: List, references: List) -> Dict:
        return self._metric.compute(predictions=predictions, references=references)
