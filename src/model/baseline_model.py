import numpy as np

from src.model.model import Model
from src.task.task import Task


class RandomBaselineModel(Model):
    def __init__(self, model_name: str, seed: int = 42):
        super().__init__(model_name)
        self.random_generator = np.random.RandomState(seed=seed)

    def predict(self, evaluation_dataset, task: Task):
        size = len(evaluation_dataset)
        choices = task.dataset.possible_ground_truths
        if len(choices) == 0:
            predictions = []
            for row in evaluation_dataset:
                choices = range(0, len(row["text"]))
                prediction = self.random_generator.choice(choices, size=1).tolist()
                predictions.extend(prediction)
        else:
            predictions = self.random_generator.choice(choices, size=size).tolist()
        return predictions

    def infer(self, rows):
        return rows

    def generate(self, rows):
        return rows

    @property
    def num_parameters(self):
        return 0
