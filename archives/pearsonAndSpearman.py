from aenum import extend_enum
import numpy as np
from scipy.stats import pearsonr, spearmanr

from lighteval.metrics import metrics
from lighteval.tasks.requests import Doc

# Ajout dynamique si nécessaire

from lighteval.metrics.utils.metric_utils import MetricCategory

from lighteval.metrics.utils.metric_utils import MetricUseCase, SampleLevelMetricGrouping

if not hasattr(MetricCategory, "CORRELATION"):
    extend_enum(MetricCategory, "CORRELATION", "CORRELATION")

if not hasattr(MetricUseCase, "SEMANTIC_SIMILARITY"):
    extend_enum(MetricUseCase, "SEMANTIC_SIMILARITY", "SEMANTIC_SIMILARITY")

def pearson_spearman_metric(predictions: list[str], formatted_doc: Doc, **kwargs) -> dict:
    try:
        if predictions and predictions[0].strip():
            response = float(predictions[0])
        else:
            response = 0.0
    except Exception:
        response = 0.0
    gold = float(formatted_doc.gold_index)
    return {
        "pearson_r": (response, gold),
        "spearman_r": (response, gold)
    }

def pearson_agg(pairs):
    preds, golds = zip(*pairs)
    return pearsonr(preds, golds)[0]

def spearman_agg(pairs):
    preds, golds = zip(*pairs)
    return spearmanr(preds, golds)[0]

pearson_spearman_metric_obj = SampleLevelMetricGrouping(
    metric_name=["pearson_r", "spearman_r"],
    higher_is_better={"pearson_r": True, "spearman_r": True},
    category=MetricCategory.CORRELATION,
    use_case=MetricUseCase.SEMANTIC_SIMILARITY,
    sample_level_fn=pearson_spearman_metric,
    corpus_level_fn={
        "pearson_r": pearson_agg,
        "spearman_r": spearman_agg,
    },
)
extend_enum(metrics.Metrics, "pearson_spearman_deprecated", pearson_spearman_metric_obj)

if __name__ == "__main__":
    print("✅ Imported pearson_spearman metric")
