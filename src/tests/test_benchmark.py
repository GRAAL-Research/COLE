from pathlib import Path

import pytest

from src.Benchmark import Benchmark
from src.Benchmarks import AllocineBench
from src.Metrics import Accuracy
from src.Models.Model import Model


class DummyModel(Model):
    def infer(self, prompt):
        return ""


class DummyBenchmark(Benchmark):
    def __init__(self, name, data):
        super().__init__(name)
        self._data = data
        self.used_split = 'test'
        self.prompt_instructions = ""

    def load_dataset(self):
        return {'test': self._data}


def test_build_prompt_defaults():
    b = Benchmark("bname")
    data = {"label": 1, "input": "foo"}
    prompt = b.build_prompt(data)
    assert "foo" in prompt
    assert "Answer with 1 for positive, or 0 for negative" in prompt


def test_get_gold_label():
    b = Benchmark("bname")
    sample = {"label": 0}
    assert b.get_gold_label(sample) == 0


def test_evaluate_full_flow():
    data = [
        {"label": 5, "input": "foo5"},
        {"label": 3, "input": "bar3"},
    ]

    bench = DummyBenchmark("bench", data)
    bench.metrics = [Accuracy()]
    bench.infer_answer = lambda test, model: test["label"]

    scores, details = bench.evaluate(DummyModel("m"))
    assert 'accuracy' in scores
    assert scores['accuracy'] == pytest.approx(1.0)
    assert isinstance(details, dict)
    for idx, record in details.items():
        assert record['gold_label'] == data[idx]['label']
        assert record['Infered'] == data[idx]['label']


def test_compare_infered_results():
    path = Path("E:/Stage/colle/src/results/mon_super_ultra_merveilleux_modele/Allocine.jsonl")
    with open(path, "r" ) as file:
        bench = AllocineBench()
        metrics  = bench.compare_infered_results(file)
        print(metrics)