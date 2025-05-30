from abc import abstractmethod

from click import prompt

import Metrics
from Model import Model
from download_datasets import load_datasets_from_huggingface, load_dataset_from_huggingface


class Benchmark:
    def __init__(self, name = "", metrics=None, prompt_instructions="", used_split="test"):
        if metrics is None:
            metrics = [Metrics.Accuracy()]
        self.name = name
        self.metrics: list[Metrics] = []
        self.used_split = used_split
        self.prompt_instructions = "Answer with 1 for positive, or 0 for negative"

    def build_prompt(self, test):
        return f"{test}. {self.prompt_instructions}"

    @abstractmethod
    def gather_test_data(self, test):
        return ""

    def evaluate(self, model: Model):
        dataset = self.load_dataset()
        results = {}
        gold_labels = []
        infered_labels = []
        print(dataset)
        for idx, test in enumerate(dataset[self.used_split]):
            infered_label = self.infer_answer(test, model)
            results[idx] = {"gold_label": self.get_gold_label(test), "Infered": infered_label}
            gold_labels.append(self.get_gold_label(test))
            infered_labels.append(infered_label)
        return self.compute(gold_labels, infered_labels), results

    @abstractmethod
    def get_gold_label(self, test):
        return test["label"]

    def load_dataset(self):
        return load_dataset_from_huggingface(self.name)

    def infer_answer(self, test, model: Model):
        prompt = self.build_prompt(test)
        answer = model.infer(prompt)
        return self.parse_answer(answer)

    # Override to implement answer modification.
    @abstractmethod
    def parse_answer(self, answer):
        return int(answer)

    def compute(self, gold_labels, infered_labels):
        results = {}
        for metric in self.metrics:
            result = metric.compute(golds=gold_labels,preds= infered_labels)
            results[metric.name] = result
        return results
