import json
import logging
import os
from datetime import datetime
from src.model.model import Model
from src.task.task import Task, Tasktype
from src.task.task_factory import tasks_factory


class ModelEvaluator:
    """The model evaluator acts as a pipeline for evaluation models on tasks available from tasks_factory."""

    def __init__(self):
        self.last_predictions = {}

        self.last_metrics = {}

    def compute_metrics(self):
        """Compute metrics over the last tested model's predictions,
        must have called one the evaluate functions before or loaded predictions with load_predictions_from_file.
        """
        metrics = []

        for task_dict in self.last_predictions["tasks"]:
            task_name, preds = list(task_dict.items())[0]
            if not preds:
                warning_message = f"Task '{task_name}' ignored due to no predictions"
                logging.warning(warning_message)
                continue
            try:
                tasks = tasks_factory([task_name])
                task = tasks[0]
                metric_score, warning = task.compute(preds)
            except Exception as e:
                error_message = f"error while calculating metrics'{task_name}' : {e}"
                logging.error(error_message)
                continue
            metric_name = task.metric_name
            task_entry = {
                task_name: {
                    metric_name: {**metric_score, f"{metric_name}_warning": warning}
                }
            }
            metrics.append(task_entry)

        self.last_metrics = metrics
        metrics = self.last_predictions
        metrics["tasks"] = self.last_metrics
        self.last_metrics = metrics
        return metrics

    def load_predictions_from_file(self, file_path):
        """Load predictions from file to compute metrics :param file_path:path to the predictions file."""

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.last_predictions = json.load(f)
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            self.last_predictions = None
        except json.JSONDecodeError:
            print(f"Invalid JSON in file: {file_path}")
            self.last_predictions = None

    def save_metrics(self, save_path):
        """Saves computed metrics to a json file.
        :param save_path : the path to which the json file will be saved"""
        if self.last_metrics is None:
            logging.info("No metrics saved")
            return None
        return self.save_object(
            save_path,
            self.last_metrics,
            f"{self.last_model_name.replace('/', '_')}_metrics.json",
            )

    def evaluate(self, model: Model, tasks: list[Task]):
        """Evaluates a given model on the given tasks.
        :param model : the model that will infer on the given tasks
        :param tasks : the tasks to be evaluated on"""
        return self.evaluate_subset(model, tasks)

    def evaluate_subset(self, model: Model, tasks: list[Task], subset_size=None):
        """Evaluates a given model on the given tasks, but only on a given size.
        :param model : the model that will infer on the given tasks
        :param tasks : the tasks to be evaluated on
        :param subset_size : the size of the subset to be evaluated"""
        predictions = []
        for task in tasks:
            try:
                if subset_size is None:
                    prompts = task.dataset.prompts[:]
                else:
                    prompts = task.dataset.prompts[:subset_size]

                if task.task_type == Tasktype.INFERENCE:
                    task_predictions = model.infer(
                        prompts, task.dataset.possible_ground_thruths
                    )
                elif task.task_type == Tasktype.GENERATIVE:
                    task_predictions = model.generate(prompts)
                else:
                    logging.error(f"unknown task type {task.task_type}")
                    task_predictions = None

                task_predictions = {task.task_name: task_predictions}
                predictions.append(task_predictions)

            except Exception as e:
                error_message = f"Tâche '{task.task_name}' échouée : {e}"
                logging.error(error_message)
                continue
        self.last_predictions = {
            "model_name": model.name,
            "model_url": "No URL provided",
            "tasks": predictions,
        }
        self.last_model_name = model.name
        return self.last_predictions

    def save_results(self, save_path):
        """Saves inferred metrics to a json file.
        :param save_path : the path to which the json file will be saved"""
        if self.last_model_name is None:
            logging.error("Please evaluate before saving results")
            return
        return self.save_object(
            save_path,
            self.last_predictions,
            f"{self.last_model_name.replace('/', '_')}_{datetime.now().strftime("%Y%m%d-%H%M")}.json",
        )

    def save_object(self, save_dir_path, saved_object, filename):
        """Utility method to save the given object into a json file."""
        os.makedirs(save_dir_path, exist_ok=True)
        full_path = os.path.join(save_dir_path, filename)
        try:
            with open(full_path, "w", encoding="utf-8") as f:
                json.dump(saved_object, f, indent=2)
            info_message = f"Results saved to {save_dir_path}"
            logging.info(info_message)
        except Exception as e:
            error_message = f"Failed to save object: {e}"
            logging.error(error_message)
        return full_path
