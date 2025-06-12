import json
from abc import abstractmethod


from src.Models.Model import Model
from src.download_datasets import load_dataset_from_huggingface
from src.BenchmarkResult import BenchmarkResult
from src.Metrics import Accuracy,Metrics


class Benchmark:
    INFERED_LABEL_KEY = "infered"
    GOLD_LABEL_KEY = "gold_label"

    def __init__(self, name="", metrics=None, used_split="test", **kwargs):
        if metrics is None:
            metrics = [Accuracy()]
        self.name = name
        self.metrics: list[Metrics] = []
        self.used_split = used_split
        self.data_path = kwargs.get("data_path", None)
        self.no_label_path = kwargs.get("no_label_path", None)


    def evaluate(self, model: Model, max_targets=None):
        print(f"Evaluating model : {model.name} on benchmark : {self.name}")
        dataset = self.load_dataset()
        results = {}
        gold_labels = []
        infered_labels = []

        for idx, test in enumerate(dataset[self.used_split]):
            infered_label = self.infer_answer(test, model)
            try:
                gold_label = self.get_gold_label(test)
            except Exception as e:
                print(f" Erreur lors de la récupération du gold label pour l’exemple {idx} : {e}")
                gold_label = None

            if infered_label is None:
                if gold_label is None:
                    infered_label = 0
                else:
                    infered_label = self.get_default_wrong_label(gold_label)

            results[idx] = {Benchmark.GOLD_LABEL_KEY: gold_label, Benchmark.INFERED_LABEL_KEY: infered_label}
            gold_labels.append(gold_label)
            infered_labels.append(infered_label)

            if max_targets is not None and len(gold_labels) >= max_targets:
                break
        metrics = self.compute(gold_labels, infered_labels)
        return metrics, results

    def load_dataset(self):
        return load_dataset_from_huggingface(self.name)

    def infer_answer(self, test, model: Model, max_retries=1):
        prompt = self.build_prompt(test)
        tries = 0
        while tries <= max_retries:
            try:
                raw_answer = model.infer(prompt)
                return self.parse_answer(raw_answer)
            except Exception as e:
                tries += 1
                if tries > max_retries:
                    print("Failed to infer answer after retries, skipping...")
                    return None



    def compute(self, gold_labels, infered_labels):
        print(f"Computing Metrics for {self.name}...")
        results = {}
        for metric in self.metrics:
            result = metric.compute(golds=gold_labels, preds=infered_labels)
            results[metric.name] = result
        return results

    @staticmethod
    def parse_benchmark_answers(file):
        infered = []
        for line in file:
            result = json.loads(line)
            infered.append(list(result.values())[0])
        return infered

    def compare_infered_results(self, infered_labels_file, start: int = 0,dataset = None):
        if dataset is None:
            dataset = self.load_dataset()

        preds = Benchmark.parse_benchmark_answers(infered_labels_file)
        golds = self.get_golds(dataset)
        try:
            golds = golds[start:start + len(preds)]
        except Exception as e:
            print("Oops, your predictions span over more than possible")
            golds = golds[0:len(preds)]
        print(preds, golds)
        return self.compute(golds, preds)

    def get_golds(self,dataset = None):
        if dataset is None:
            dataset = self.load_dataset()
        return [self.get_gold_label(test) for test in dataset[self.used_split]]


    @abstractmethod
    def get_default_wrong_label(self, gold_label):
        return 0

    @abstractmethod
    def get_gold_label(self, test):
        return test["label"]

    @abstractmethod
    def build_prompt(self, test):
        return f"{test}. No prompt given"

    # Override to implement answer modification.
    @abstractmethod
    def parse_answer(self, answer):
        return int(answer)
