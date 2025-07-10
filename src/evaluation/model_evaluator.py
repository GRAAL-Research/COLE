import json
import logging
import os
from datetime import datetime
from src.model.model import Model
from src.task.task import Task
from src.task.task_factory import tasks_factory


class ModelEvaluator:
    """The model evaluator acts as a pipeline for evaluation models on tasks available from tasks_factory"""

    def __init__(self):
        self.last_predictions = {}
        self.last_model_name = None
        self.last_metrics = {}

    def compute_metrics(self):
        """compute metrics over last tested model's predictions, must have called one the evaluate functions before"""
        metrics = {}
        for key, value in self.last_predictions.items():
            tasks = tasks_factory({"tasks": [{key: value}]})
            metrics[key] = tasks[0].compute(value)
        self.last_metrics = metrics
        return metrics

    def save_metrics(self, save_path):
        """saves computed metrics to a json file
        :param save_path : the path to which the json file will be saved"""
        if self.last_metrics is None:
            logging.info("No metrics saved")
            return
        else:
            self.save_object(
                save_path,
                self.last_metrics,
                f"{self.last_model_name.replace('/', '_')}_metrics.json",
            )

    def evaluate(self, model: Model, tasks: list[Task]):
        """evaluates a given model on the given tasks
        :param model : the model that will infer on the given tasks
        :param tasks : the tasks to be evaluated on"""
        self.evaluate_subset(model, tasks)

    def evaluate_subset(self, model: Model, tasks: list[Task], subset_size=None):
        """evaluates a given model on the given tasks, but only on a given size.
        :param model : the model that will infer on the given tasks
        :param tasks : the tasks to be evaluated on
        :param subset_size : the size of the subset to be evaluated"""
        self.last_predictions = {}
        for task in tasks:
            if subset_size is None:
                prompts = task.dataset.prompts[0:]
            else:
                prompts = task.dataset.prompts[0:subset_size]
            preds = model.infer(prompts, task.dataset.possible_ground_thruths)

            self.last_predictions[task.task_name] = preds
        self.last_model_name = model.name
        return self.last_predictions

    def save_results(self, save_path):
        """saves inferred metrics to a json file
        :param save_path : the path to which the json file will be saved"""
        if self.last_model_name is None:
            logging.error("Please evaluate before saving results")
            return
        self.save_object(
            save_path,
            self.last_predictions,
            f"{self.last_model_name.replace('/', '_')}_{datetime.now().strftime("%Y%m%d-%H%M")}.json",
        )

    def save_object(self, save_path, saved_object, filename):
        """Utility method to save the given object into a json file"""
        os.makedirs(save_path, exist_ok=True)
        full_path = os.path.join(save_path, filename)
        try:
            with open(full_path, "w") as f:
                json.dump(saved_object, f, indent=2)
            logging.info(f"Results saved to {save_path}")
        except Exception as e:
            logging.error(f"Failed to save object: {e}")
