import os
from concurrent.futures import ThreadPoolExecutor
from typing import Union, List

from datasets import Dataset
from datasets.formatting.formatting import LazyRow
from tqdm import tqdm

from cole.language_model.language_model_abstraction import LanguageModel
from cole.language_model.private_language_model_factory import (
    private_language_model_factory,
)
from cole.task.task import Task, TaskType


class RemoteLLMModel(LanguageModel):
    """
    LLM Model based on private remote LLM provider (e.g. OpenAI) and pipeline mechanism for inference.
    """

    def generate(self, rows: LazyRow) -> Union[str, List[str]]:
        try:
            generate = self.model.predict(rows["text"])
        except:
            generate = "NA"
            print("Generated a NA when model inference.")
        return generate

    def infer(self, rows: LazyRow) -> Union[str, List[str]]:
        try:
            infer = self.model.predict(rows["text"])
        except:
            infer = "NA"
            print("Generated a NA when model inference.")
        return infer

    def __init__(
        self,
        model_name: str,
        token: Union[str, None] = None,
    ):
        super().__init__(model_name)
        self._model_name = model_name
        self._token = token

        self.model = private_language_model_factory(model_name=self._model_name)

    def predict(self, evaluation_dataset: Dataset, task: Task) -> List:
        if task.task_type == TaskType.INFERENCE:
            labels = task.dataset.possible_ground_truths
            self.model.init_function_calling(
                labels, tool_choices=self.model.tool_choices
            )
            inference_fn = self.infer
        else:
            inference_fn = self.generate

        workers = int(os.getenv("COLE_WORKERS", "1"))
        if workers > 1:
            return self._predict_parallel(evaluation_dataset, workers)

        process_dataset = evaluation_dataset.map(
            inference_fn,
            batched=False,
            desc=f"Running evaluation for task: {task.task_name}",
            remove_columns="text",
        )

        self.model.print_none()

        return list(process_dataset["prediction"])

    def _predict_parallel(self, evaluation_dataset: Dataset, workers: int) -> List:
        """Appelle l'API avec `workers` requêtes simultanées (les appels sont
        limités par la latence réseau, pas par le CPU)."""

        def call(text: str):
            try:
                return self.model.predict(text)["prediction"]
            except Exception:  # pylint: disable=broad-exception-caught
                return "NA"

        with ThreadPoolExecutor(max_workers=workers) as pool:
            predictions = list(
                tqdm(
                    pool.map(call, evaluation_dataset["text"]),
                    total=len(evaluation_dataset),
                    desc=f"Parallel inference ({workers} workers)",
                )
            )
        self.model.print_none()
        return predictions
