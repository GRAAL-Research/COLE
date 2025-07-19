import abc
import logging
from typing import Union, List

import torch
from transformers import (
    pipeline,
)

from src.model.model import Model
from src.model.model_factory import model_tokenizer_factory


def chunk_list(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i : i + chunk_size]


def omit_none(**kwargs):
    return {k: v for k, v in kwargs.items() if v is not None}


class HFModel(Model, abc.ABC):
    """
    Model based on Hugging Face Transformers and pipeline mechanism,
    loads pretrained models and uses them for inference and generation.
    """

    def __init__(
        self,
        model_name: str,
        token: Union[str, None] = None,
        lazy_load: bool = True,
        batch_size: int = 8,
    ):
        super().__init__(model_name)
        self._model_name = model_name
        self.model, self.tokenizer, self.pipe, self.loaded = None, None, None, False
        self._token = token
        self._batch_size = batch_size
        if not lazy_load:
            self.create_pipeline()

    @abc.abstractmethod
    def generate(self, prompts: str, conditions=None) -> Union[str, List[str]]:
        raise NotImplementedError

    def infer(self, prompts: str, possible_answers, conditions=None):
        """
        Takes a list of prompts as input and uses its loaded model to generate predictions.
        """
        if not self.loaded:
            self.create_pipeline()
        if isinstance(prompts, str):
            prompts = [prompts]

        all_outputs = []
        for sub_batch in chunk_list(prompts, self._batch_size):
            try:
                outputs = self.pipe(sub_batch)
            except Exception as e:
                error_message = f"Error during inference {sub_batch[:2]} : {e}"
                logging.error(error_message)
                outputs = [{} for _ in sub_batch]
            all_outputs.extend(outputs)

        return all_outputs

    def create_pipeline(self):
        try:
            self.model, self.tokenizer = model_tokenizer_factory(
                model_name=self._model_name,
                max_seq_length=4096,
                huggingface_token=self._token,
                gpu_memory_utilization=0.75,
            )

            self.pipe = pipeline(
                task="text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
            )
            self.loaded = True
        except Exception as e:
            error_message = f"️ Impossible to load model {self._model_name} : {e}"
            logging.error(error_message)
            self.loaded = False

    def unload_model(self):
        self.tokenizer, self.model, self.pipe = None, None, None
        self.loaded = False


class HFLLMModel(HFModel):
    """
    LLM Model based on Hugging Face Transformers and pipeline mechanism, loads pretrained LLM models and uses
    it for inference.
    """

    def __init__(
        self,
        max_gen_length=5,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.max_gen_length = max_gen_length

    def generate(self, prompts: Union[str, List[str]], conditions=None):
        """
        Takes a list of prompts as input and uses its loaded model to generate predictions.
        """
        if not self.loaded:
            self.create_pipeline()
        if isinstance(prompts, str):
            prompts = [prompts]
        all_texts = []
        for sub_batch in chunk_list(prompts, self._batch_size):
            try:
                batch_outputs = self.pipe(
                    sub_batch,
                    max_new_tokens=self.max_gen_length,
                )
            except Exception as e:
                logging.error(e)
                batch_outputs = [{} for _ in sub_batch]
            for single_output in batch_outputs:
                if isinstance(single_output, list) and len(single_output) > 0:
                    all_texts.append(single_output[0].get("generated_text", ""))
                else:
                    text = (
                        single_output.get("generated_text", "")
                        if isinstance(single_output, dict)
                        else ""
                    )
                    all_texts.append(text)
        return all_texts

    def infer(self, prompts: Union[str, List[str]], possible_answers, conditions=None):
        """
        Takes a list of prompts as input and uses its loaded model to generate predictions.
        """
        if not self.loaded:
            self.create_pipeline()
        if isinstance(prompts, str):
            prompts = [prompts]
        all_answers = []
        for sub_batch in chunk_list(prompts, self._batch_size):
            try:

                labels = batch_score_labels(
                    sub_batch, possible_answers, self.model, self.tokenizer
                )
                all_answers.extend(labels)
            except Exception as e:
                error_message = f"Error occurred while processing batch : {e}"
                logging.error(error_message)

        return all_answers


def batch_score_labels(prompts, candidate_labels, model, tokenizer):
    device = model.device
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    all_scores = []

    for label in candidate_labels:
        label_str = " " + str(label).strip()
        full_prompts = [p.rstrip() + label_str for p in prompts]

        # Tokenize original prompts to get lengths
        n_positions = getattr(model.config, "n_positions", None) or getattr(
            model.config, "max_position_embeddings", None
        )
        prompt_inputs = tokenizer(
            prompts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=n_positions,
        ).to(device)

        full_inputs = tokenizer(
            full_prompts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=n_positions,
        ).to(device)

        with torch.no_grad():
            logits = model(**full_inputs).logits  # [batch, seq_len, vocab]
            log_probs = torch.nn.functional.log_softmax(logits, dim=-1)

        batch_scores = []
        for i in range(len(prompts)):
            input_ids = full_inputs.input_ids[i]
            prompt_len = (
                (prompt_inputs.input_ids[i] != tokenizer.pad_token_id).sum().item()
            )

            label_ids = input_ids[prompt_len:]  # label tokens only
            if len(label_ids) == 0:
                batch_scores.append(float("-inf"))
                continue

            try:
                score = sum(
                    log_probs[i, prompt_len + j - 1, token_id].item()
                    for j, token_id in enumerate(label_ids)
                )
                batch_scores.append(score)
            except IndexError:
                batch_scores.append(float("-inf"))

        all_scores.append(batch_scores)

    scores_tensor = torch.tensor(all_scores, device=device).mT  # shape: [batch, labels]
    top_indices = torch.argmax(scores_tensor, dim=1)
    predicted = [candidate_labels[i] for i in top_indices]

    return predicted
