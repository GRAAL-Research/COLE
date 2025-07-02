import logging
import re

import numpy as np
from aenum import extend_enum
from lighteval.metrics.metrics import Metrics
from lighteval.metrics.metrics_sample import LoglikelihoodAcc
from lighteval.metrics.utils.metric_utils import (
    SampleLevelMetric,
    MetricCategory,
    MetricUseCase,
    CorpusLevelMetric,
)
from lighteval.tasks.requests import Doc


def wrapper(*args, **kwargs):
    return LoglikelihoodAcc(logprob_normalization=None).compute(*args, **kwargs)


accuracy_wrapper = SampleLevelMetric(
    metric_name="acc",
    sample_level_fn=wrapper,
    category=MetricCategory.MULTICHOICE,
    use_case=MetricUseCase.ACCURACY,
    corpus_level_fn=np.mean,
    higher_is_better=True,
)

from scipy.stats import pearsonr, spearmanr


def pearson_spearman_sample_preparator(
    golds, predictions, formatted_doc: Doc, **kwargs
):
    return {
        "gold": float(formatted_doc.choices[formatted_doc.gold_index]),
        "preds": pearson_spearman_parse(predictions),
    }


def pearson_spearman_parse(predictions):
    number = 0
    for pred in predictions:
        match = re.search(r"[-+]?\d*\.\d+|\d+", pred)
        if match and number == 0:
            return float(match.group())
        else:
            number = 0
    return number


def pearson_spearman_metric(items, **kwargs) -> dict:
    # Convert predictions to float
    preds = [sample["preds"] for sample in items]
    golds = [sample["gold"] for sample in items]
    if len(preds) < 2:
        int()
        return {
            "pearson": 0.0,
            "spearman": 0.0,
        }  # Can't compute correlation with <2 points

    pearson_corr = float(pearsonr(preds, golds)[0])
    spearman_corr = float(spearmanr(preds, golds)[0])
    return {"pearson": pearson_corr, "spearman": spearman_corr}


pearson = CorpusLevelMetric(
    metric_name="pearson",
    sample_level_fn=pearson_spearman_sample_preparator,
    category=MetricCategory.GENERATIVE,
    use_case=MetricUseCase.ACCURACY,
    corpus_level_fn=pearson_spearman_metric,
    higher_is_better=True,
)


def add_custom_metrics_to_lighteval():
    extend_enum(Metrics, "pearson_spearman", pearson)
    extend_enum(Metrics, "accuracy_wrapper", accuracy_wrapper)
    logging.info(f"Imported custom metrics.")


