import json
import logging
import os
from datetime import datetime

from src.model.hugging_face_model import HFLLMModelClassifier
from src.model.model import Model

from src.task.task import Task
from src.task.task_factory import tasks_factory


class ModelEvaluator:
    def __init__(self):
        self.last_predictions = {}
        self.last_model_name = None
        self.last_metrics = {}
    def compute_metrics(self):
        metrics = {}
        for key,value in self.last_predictions.items():
            tasks = tasks_factory({"tasks" : [{key:value}]})
            metrics[key] = tasks[0].compute(value)
        self.last_metrics = metrics
        return metrics

    def save_metrics(self, save_path):
        if self.last_metrics is None:
            logging.info("No metrics saved")
            return
        else:
            self.save_object(save_path,self.last_metrics, f"{self.last_model_name.replace('/', '_')}_metrics.json")

    def evaluate(self, model: Model, tasks: list[Task]):
        self.evaluate_subset(model, tasks)

    def evaluate_subset(self, model: Model, tasks : list[Task], subset_size=None):
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
        if self.last_model_name is None:
            logging.error("Please evaluate before saving results")
            return
        self.save_object(save_path, self.last_predictions,f"{self.last_model_name.replace('/', '_')}_{datetime.now().strftime("%Y%m%d-%H%M")}.json")

    def save_object(self, save_path, saved_object,filename):
        os.makedirs(save_path, exist_ok=True)
        full_path = os.path.join(save_path,filename)
        try:
            with open(full_path, "w") as f:
                json.dump(saved_object, f, indent=2)
            logging.info(f"Results saved to {save_path}")
        except Exception as e:
            logging.error(f"Failed to save object: {e}")


tasks = tasks_factory({"tasks" : [{"allocine":""},{"qfrcola":""},{"xnli":""},]})
models = ["OpenLLM-France/Lucie-7B",
        "OpenLLM-France/Lucie-7B-Instruct-v1.1",]

for model_name in models:
    model = HFLLMModelClassifier(model_name, batch_size=16)
    evaluator = ModelEvaluator()
    evaluator.evaluate_subset(model, tasks, 32)
    evaluator.save_results("./results")
    evaluator.compute_metrics()
    evaluator.save_metrics("./results")




