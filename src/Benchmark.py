from abc import abstractmethod

import Metrics
from Models.Model import Model
from download_datasets import load_dataset_from_huggingface


class Benchmark:
    INFERED_LABEL_KEY = "infered"
    GOLD_LABEL_KEY = "gold_label"

    def __init__(self, name="", metrics=None, prompt_instructions="", used_split="test", **kwargs):
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
            try:
                infered_label = self.infer_answer(test, model)
            except Exception as e:
                print(f" Erreur lors de l’inférence pour l’exemple {idx} : {e}")
                gold_label_tmp = None
                try:
                    gold_label_tmp = self.get_gold_label(test)
                except Exception:
                    gold_label_tmp = None
                infered_label = (
                    self.get_default_wrong_label(gold_label_tmp)
                    if gold_label_tmp is not None
                    else 0
                )

            try:
                gold_label = self.get_gold_label(test)
            except Exception as e:
                print(f" Erreur lors de la récupération du gold label pour l’exemple {idx} : {e}")
                gold_label = None

            if infered_label is None:
                infered_label = (
                    self.get_default_wrong_label(gold_label)
                    if gold_label is not None
                    else 0
                )

            results[idx] = {Benchmark.GOLD_LABEL_KEY: gold_label, Benchmark.INFERED_LABEL_KEY: infered_label}
            gold_labels.append(gold_label)
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

    @staticmethod
    def parse_benchmark_answers(file):
        infered = []
        for line in file:
            result = json.loads(line)
            infered.append(list(result.values())[0])
        return infered

    def compare_infered_results(self, infered_labels_file, start: int = 0):
        dataset = self.load_dataset()

        preds = Benchmark.parse_benchmark_answers(infered_labels_file)
        golds = [self.get_gold_label(test) for test in dataset[self.used_split]]
        try:
            golds = golds[start:start + len(preds)]
        except Exception as e:
            print("Oops, your predictions span over more than possible")
            golds = golds[0:len(preds)]
        return self.compute(golds, preds)

    @abstractmethod
    def get_default_wrong_label(self, gold_label):
        return 0
