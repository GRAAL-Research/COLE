import pytest
from archives.BenchmarkSuite import BenchmarkSuite

# Modèles et benchmarks factices pour simuler le comportement
class DummyModel:
    def __init__(self, name):
        self.model_name = name

class DummyBenchmark:
    def __init__(self, name, return_value):
        self.name = name
        self._return = return_value

    def evaluate(self, model):
        return self._return


def test_compute_all_multiple_models_and_benchmarks():
    m1 = DummyModel("model1")
    m2 = DummyModel("model2")
    b1 = DummyBenchmark("benchA", ("resA", {"label": 1}))
    b2 = DummyBenchmark("benchB", ("resB", {"label": 2}))

    suite = BenchmarkSuite(models=[m1, m2], benchmarks=[b1, b2])
    out = suite.compute_all()

    expected = {
        "model1": {
            "benchA": ("resA", {"label": 1}),
            "benchB": ("resB", {"label": 2}),
        },
        "model2": {
            "benchA": ("resA", {"label": 1}),
            "benchB": ("resB", {"label": 2}),
        },
    }
    assert out == expected


def test_evaluate_model_single_model():
    m = DummyModel("solo")
    b1 = DummyBenchmark("benchX", ("rx", {}))
    b2 = DummyBenchmark("benchY", ("ry", {}))

    suite = BenchmarkSuite(benchmarks=[b1, b2])
    out = suite.evaluate_model(m)

    assert out == {
        "benchX": ("rx", {}),
        "benchY": ("ry", {}),
    }


def test_compute_1_model_per_bench_model_with_missing_model():
    m1 = DummyModel("m1")
    b1 = DummyBenchmark("B1", ("r1", {}))
    b2 = DummyBenchmark("B2", ("r2", {}))

    suite = BenchmarkSuite(models=[m1, None], benchmarks=[b1, b2])
    out = suite.compute_1_model_per_bench_model()

    assert out == {
        "B1": ("r1", {}),
        "B2": "(no model)",
    }
