import abc
from typing import Union, List

import torch
from datasets import Dataset
from transformers import (
    pipeline,
)

from src.model.model import Model
from src.model.model_factory import model_tokenizer_factory
from src.task.task import TaskType, Task


class HFModel(Model, abc.ABC):
    """
    Model based on Hugging Face Transformers and pipeline mechanism,
    loads pretrained models and uses them for inference and generation.
    """

    def __init__(
        self,
        model_name: str,
        token: Union[str, None] = None,
        batch_size: int = 8,
    ):
        super().__init__(model_name)
        self._model_name = model_name
        self._token = token

        self.model, self.tokenizer = model_tokenizer_factory(
            model_name=self._model_name,
            huggingface_token=self._token,
        )

        num_params = self.model.num_parameters()

        # To handle max batch size for these models.
        if num_params >= 70000000000:  # 70B
            batch_size = 8
        if num_params >= 32000000000:  # 32B
            batch_size = 16
        elif num_params >= 27000000000:  # 27B
            batch_size = 32
        self._batch_size = batch_size


class HFLLMModel(HFModel):
    """
    LLM Model based on Hugging Face Transformers and pipeline mechanism, loads pretrained LLM models and uses
    it for inference.
    """

    def predict(self, evaluation_dataset: Dataset, task: Task) -> List:
        if task.task_type == TaskType.INFERENCE:
            labels = task.dataset.possible_ground_truths
            self.pipeline = pipeline(
                task="zero-shot-classification",
                model=self.model,
                tokenizer=self.tokenizer,
                batch_size=self._batch_size,
                torch_dtype="float16",
                return_full_text=False,
                max_new_tokens=16,
                padding=True,
                truncation=True,
                max_length=4096,
                candidate_labels=labels,
            )
            if len(labels) == 2:
                inference_fn = self.infer_binary
            else:
                inference_fn = self.infer
        else:
            self.pipeline = pipeline(
                task="text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                batch_size=self._batch_size,
                torch_dtype="float16",
                return_full_text=False,
                max_new_tokens=64,
                padding=True,
                truncation=True,
                max_length=4096,
            )
            inference_fn = self.generate

        process_dataset = evaluation_dataset.map(
            inference_fn,
            batched=True,
            batch_size=self._batch_size,
            desc=f"Running evaluation for task: {task.task_name}",
            remove_columns="text",
        )

        return process_dataset["prediction"]

    def generate(self, rows):
        """
        Do a generation over a set of rows and extract the generated text and apply string post-processing.
        """

        with torch.no_grad():
            text = rows["text"]

            outputs = self.pipeline(text)
            generated_texts = [
                output[0]["generated_text"].strip() for output in outputs
            ]

        return {"prediction": generated_texts}

    def infer(self, rows):
        """
        Do a zero-shot classification and extract the label using a per-element generation.

        For a fucking strange reason, the pipeline does not work in this case:
        1. Batched generation of more than one element
        2. More than 2 labels.

        Thus, we need to loop over the element. Painful I know.
        """

        with torch.no_grad():
            texts = rows["text"]

            classifications = []
            for text in texts:
                output = self.pipeline(text)
                classifications.append(
                    output["labels"][0]
                )  # Labels are sorted in likelihood order.

        return {"prediction": classifications}

    def infer_binary(self, rows):
        """
        Do a binary zero-shot classification and extract the label using a per-element generation.
        """
        with torch.no_grad():
            texts = rows["text"]

            outputs = self.pipeline(texts)
            classifications = [
                output["labels"][0] for output in outputs
            ]  # Labels are sorted in likelihood order.

        return {"prediction": classifications}
