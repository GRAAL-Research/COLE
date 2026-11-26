import logging
import os
import time
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
            generate = self.model.predict(rows["text"], extract_label=False)
        except Exception:  # pylint: disable=broad-exception-caught
            generate = {"prediction": "NA"}
            print("Generated a NA when model inference.")
        return generate

    def infer(self, rows: LazyRow) -> Union[str, List[str]]:
        try:
            infer = self.model.predict(rows["text"])
        except Exception:  # pylint: disable=broad-exception-caught
            infer = {"prediction": "NA"}
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
            # Do not carry the tools/tool_choice of a previous classification task.
            self.model.reset_function_calling()
            inference_fn = self.generate

        if os.getenv("COLE_BATCH") == "1" and hasattr(self.model, "client"):
            if "claude" in self._model_name.lower():
                return self._predict_anthropic_batch(
                    evaluation_dataset,
                    extract_label=task.task_type == TaskType.INFERENCE,
                )

        workers = int(os.getenv("COLE_WORKERS", "1"))
        if workers > 1:
            return self._predict_parallel(evaluation_dataset, workers, inference_fn)

        process_dataset = evaluation_dataset.map(
            inference_fn,
            batched=False,
            desc=f"Running evaluation for task: {task.task_name}",
            remove_columns="text",
        )

        self.model.print_none()

        return list(process_dataset["prediction"])

    def _predict_parallel(
        self, evaluation_dataset: Dataset, workers: int, inference_fn
    ) -> List:
        """Appelle l'API avec `workers` requêtes simultanées (les appels sont
        limités par la latence réseau, pas par le CPU). Réutilise `inference_fn`
        (infer ou generate) pour garder le même post-traitement que le chemin
        séquentiel."""

        def call(text: str):
            return inference_fn({"text": text})["prediction"]

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

    def _predict_anthropic_batch(
        self,
        evaluation_dataset: Dataset,
        extract_label: bool,
        chunk_size: int = 5000,
        poll_seconds: int = 30,
    ) -> List:
        """Évalue une tâche avec l'API Message Batches d'Anthropic (50 % moins chère,
        asynchrone). Les lots sont soumis par tranches de `chunk_size` requêtes puis
        interrogés jusqu'à leur fin; une requête échouée, annulée ou expirée donne la
        prédiction « NA », comme le chemin synchrone."""
        client = self.model.client
        texts = evaluation_dataset["text"]
        params_base = {
            "model": self.model.model_name,
            **self.model._extra_params,  # pylint: disable=protected-access
        }

        batch_ids = []
        for start in range(0, len(texts), chunk_size):
            requests = [
                {
                    "custom_id": str(i),
                    "params": {
                        **params_base,
                        "messages": self.model.format_prompt(texts[i]),
                    },
                }
                for i in range(start, min(start + chunk_size, len(texts)))
            ]
            batch = client.messages.batches.create(requests=requests)
            batch_ids.append(batch.id)
            logging.info(
                "Submitted Anthropic batch %s (%d requests)", batch.id, len(requests)
            )

        predictions = ["NA"] * len(texts)
        for batch_id in batch_ids:
            while (
                client.messages.batches.retrieve(batch_id).processing_status != "ended"
            ):
                time.sleep(poll_seconds)
            for entry in client.messages.batches.results(batch_id):
                if entry.result.type == "succeeded":
                    predictions[int(entry.custom_id)] = (
                        self.model.extract_final_prediction(
                            entry.result.message, extract_label=extract_label
                        )
                    )
        self.model.print_none()
        return predictions
