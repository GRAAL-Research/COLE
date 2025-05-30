import pytest
from Metrics import MetricCollection, Accuracy, F1, MatthewsCC, Pearson, SpearmanR

@pytest.mark.parametrize(
    "MetricClass, args",
    [
        (Accuracy, ()),
        (F1, ()),
        (F1, ("macro",)),
        (MatthewsCC, ()),
        (Pearson, ()),
        (SpearmanR, ()),
    ],
)
def test_compute_all_real_metrics_perfect(MetricClass, args):

    m = MetricClass(*args)
    result = MetricCollection([m]).compute_all([1, 2, 3], [1, 2, 3])
    assert result[m.name] == pytest.approx(1.0)

@ pytest.mark.parametrize(
    "MetricClass, args, golds, preds, expected",
    [
        (Accuracy, (), [0, 1, 1, 0], [0, 1, 0, 1], 0.5),
        (F1, (), [0, 1, 1, 0], [0, 1, 0, 1], 0.5),
        (F1, ("macro",), [0, 1, 1, 0], [0, 1, 0, 1], 0.5),
        (MatthewsCC, (), [0, 1, 1, 0], [0, 1, 0, 1], 0.0),
        (Pearson, (), [0, 1, 1, 0], [0, 1, 0, 1], 0.0),
        (SpearmanR, (), [0, 1, 1, 0], [0, 1, 0, 1], 0.0),
    ],
)
def test_compute_all_real_metrics_imperfect(MetricClass, args, golds, preds, expected):

    m = MetricClass(*args)
    result = MetricCollection([m]).compute_all(golds, preds)
    assert result[m.name] == pytest.approx(expected)
