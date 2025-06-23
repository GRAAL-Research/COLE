import numpy as np
from aenum import extend_enum
from lighteval.metrics.metrics import Metrics
from lighteval.metrics.metrics_sample import LoglikelihoodAcc
from lighteval.metrics.utils.metric_utils import SampleLevelMetric, MetricCategory, MetricUseCase




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