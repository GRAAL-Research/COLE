import numpy as np
from aenum import extend_enum
from lighteval.metrics.metrics import Metrics
from lighteval.metrics.metrics_corpus import CorpusLevelF1Score
from lighteval.metrics.metrics_sample import LoglikelihoodAcc
from lighteval.metrics.sample_preparator import LogprobCorpusMetricInput, LoglikelihoodPreparator
from lighteval.metrics.utils.metric_utils import SampleLevelMetric, MetricCategory, MetricUseCase, CorpusLevelMetric

from src.Metrics import Pearson


def wrapper (*args, **kwargs):
    print(args)
    return LoglikelihoodAcc(logprob_normalization=None).compute(*args,**kwargs)
accuracy_wrapper = SampleLevelMetric(
        metric_name="acc",
        sample_level_fn=wrapper,
        category=MetricCategory.MULTICHOICE,
        use_case=MetricUseCase.ACCURACY,
        corpus_level_fn=np.mean,
        higher_is_better=True,
    )

extend_enum(Metrics,"accuracy_wrapper",accuracy_wrapper)

from scipy.stats import pearsonr, spearmanr

def pearson_spearman_metric(items : list[LogprobCorpusMetricInput], **kwargs) -> dict:
    # Convert predictions to float
    golds = [i.golds for i in items]
    preds = [i.preds for i in items] # or gold_score if you defined one

    if len(preds) < 2:
        int()
        return {"pearson": 0.0, "spearman": 0.0}  # Can't compute correlation with <2 points
    print(golds)
    print(preds)

    pearson_corr = pearsonr(preds, golds)
    print(pearson_corr)
    return pearson_corr,


def compute_pearson(*args, **kwargs):
    print("args : ",args)
    print("kwargs : ", kwargs)
    return 0

pearson = CorpusLevelMetric(
    metric_name="pearson",
    sample_level_fn=LoglikelihoodPreparator().prepare,
    category=MetricCategory.MULTICHOICE,
    use_case=MetricUseCase.ACCURACY,
    corpus_level_fn=pearson_spearman_metric,
    higher_is_better=True,
)
extend_enum(Metrics,"pearson",pearson)