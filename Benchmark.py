import os
from abc import abstractmethod

import pandas as pd

import Metrics
from Model import Model
from PromptBuilder import PromptBuilder
from download_datasets import load_datasets_from_huggingface, load_dataset_from_huggingface


class Benchmark:
    def __init__(self, name="", metrics=None, prompt_instructions="", used_split="test",**kwargs):
        if metrics is None:
            metrics = [Metrics.Accuracy()]
        self.name = name
        self.metrics: list[Metrics] = []
        self.used_split = used_split
        self.prompt_instructions = "Answer with 1 for positive, or 0 for negative"
        self.data_path = kwargs.get("data_path", None)

        self.no_label_path = kwargs.get("no_label_path", None)

    @abstractmethod
    def build_prompt(self, test):
        return f"{test}. {self.prompt_instructions}"

    def evaluate(self, model: Model, max_targets=None):
        print("Evaluating model")
        dataset = self.load_dataset()
        results = {}
        gold_labels = []
        infered_labels = []

        for idx, test in enumerate(dataset[self.used_split]):
            infered_label = self.infer_answer(test, model)
            gold_label = self.get_gold_label(test)
            if infered_label is None:
                infered_label = self.get_default_wrong_label(gold_label)

            results[idx] = {"gold_label": gold_label, "Infered": infered_label}
            gold_labels.append(self.get_gold_label(test))
            infered_labels.append(infered_label)

            if max_targets is not None and len(gold_labels) >= max_targets:
                break

        return self.compute(gold_labels, infered_labels), results

    @abstractmethod
    def get_gold_label(self, test):
        return test["label"]

    def load_dataset(self):
        return load_dataset_from_huggingface(self.name)

    def infer_answer(self, test, model: Model, max_retries=1):

        prompt = self.build_prompt(test)
        tries = 0
        answer = None
        succeeded = False
        while tries <= max_retries and not succeeded:
            try:
                answer = model.infer(prompt)
            except Exception as e:
                print("Failed to infer answer, skipping...")
                break
            try:
                answer = self.parse_answer(answer)
                succeeded = True
            except Exception as e:
                tries += 1
                answer = None

        return answer

    # Override to implement answer modification.
    @abstractmethod
    def parse_answer(self, answer):
        return int(answer)

    def compute(self, gold_labels, infered_labels):
        print(f"Computing Metrics for {self.name}...")
        results = {}
        for metric in self.metrics:
            result = metric.compute(golds=gold_labels, preds=infered_labels)
            results[metric.name] = result
        return results
    @abstractmethod
    def get_default_wrong_label(self, gold_label):
        return 0

