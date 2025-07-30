from src.task.task import Task
from src.model.model import Model
import numpy as np


class ConstantBaselineLLMModel(Model):
    def __init__(self, model_name, constant_value):
        super().__init__(model_name)
        self.constant_value = constant_value

    def predict(self, evaluation_dataset, task: Task):
        return [self.constant_value] * len(evaluation_dataset)

    def infer(self, rows):
        return rows

    def generate(self, rows):
        return rows
