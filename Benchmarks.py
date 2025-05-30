import Metrics
from Benchmark import Benchmark


class FrColaBench(Benchmark):

    def gather_test_data(self, test):
        return test["sentence"]

    def get_gold_label(self, test):
        return test["label"]

    def parse_answer(self, answer):
        return answer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "frcola"
        self.metrics = [Metrics.Accuracy()]
        self.prompt_instructions = "Answer with 1 if the sentence is correct, 0 otherwise"