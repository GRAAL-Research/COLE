import logging

import numpy as np
import torch

from transformers import AutoModel, pipeline, AutoTokenizer, AutoModelForCausalLM


from model import Model

MODEL_CACHE = "./Loaded_Models"


def chunk_list(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i : i + chunk_size]


def omit_none(**kwargs):
    return {k: v for k, v in kwargs.items() if v is not None}


class HFModel(Model):
    """
    Model based on Hugging Face Transformers and pipeline mechanism, loads pretrained models and uses it for inference.
    """

    def __init__(
        self,
        model_name,
        task="text-generation",
        token=None,
        lazy_load=True,
        batch_size=8,
    ):
        super().__init__(model_name)
        self.model_name = model_name
        self.model, self.tokenizer, self.pipe, self.loaded = None, None, None, False
        self.task = task
        self.token = token
        self.batch_size = batch_size
        if not lazy_load:
            self.load_model(model_name, task=task, token=token)

    def create_model(self, model_name, token=None):
        """creates the model by fetching by name on Hugging Face"""
        args = self.get_model_args(token)
        new_model = AutoModel.from_pretrained(model_name, **args)
        return new_model

    def get_model_args(self, token):
        return omit_none(use_auth_token=token, cache_dir=MODEL_CACHE,trust_remote_code=True)

    def create_tokenizer(self, model_name, token=None):
        """Creates an adapted tokenizer from Hugging Face"""
        args = omit_none(
            use_auth_token=token,
        )
        tokenizer = AutoTokenizer.from_pretrained(model_name, **args)
        return tokenizer

    def infer(self, prompts: str, possible_answers, conditions=None):
        """Takes a list of prompts as input and uses its loaded model to generate predictions."""
        if not self.loaded:
            self.load_model(self.model_name, task=self.task, token=self.token)
        if isinstance(prompts, str):
            prompts = [prompts]

        all_outputs = []
        for sub_batch in chunk_list(prompts, self.batch_size):
            try:
                outputs = self.pipe(sub_batch)
            except Exception as e:
                logging.error(f" Échec inference batch {sub_batch[:2]} : {e}")
                outputs = [{} for _ in sub_batch]
            all_outputs.extend(outputs)

        return all_outputs

    def change_task(self, task):
        """changes the inside pipeline task, to see available tasks go to https://huggingface.co/docs/transformers/main_classes/pipelines"""
        try:
            self.pipe.task = task
        except Exception:
            logging.error(f"Failed to change task to {task}")

    def load_model(self, model_name, task, token):
        try:
            self.model = self.create_model(model_name, token)
            self.tokenizer = self.create_tokenizer(model_name, token)
            self.pipe = pipeline(
                task=task,
                model=self.model,
                tokenizer=self.tokenizer,
                return_full_text=False,
            )
            self.loaded = True
        except Exception as e:
            logging.error(f"️ Impossible de charger le modèle {model_name} : {e}")
            self.loaded = False

    def unload_model(self):
        self.tokenizer, self.model, self.pipe = None, None, None
        self.loaded = False


class HFLLMModelGenerative(HFModel):
    """
    Model based on Hugging Face Transformers and pipeline mechanism, loads pretrained LLM models and uses it for inference.
    """

    def __init__(self, model_name, token=None, batch_size=8,task="text-generation",max_gen_length=3):
        super().__init__(model_name, task, token, batch_size=batch_size)
        self.max_gen_length = max_gen_length
    def create_model(self, model_name, token=None):
        args = self.get_model_args(token)
        model = AutoModelForCausalLM.from_pretrained(model_name, **args)
        return model

    def infer(self, prompts: str | list[str], possible_answers, conditions=None):
        """Takes a list of prompts as input and uses its loaded model to generate predictions."""
        if not self.loaded:
            self.load_model(self.model_name, task=self.task, token=self.token)
        if isinstance(prompts, str):
            prompts = [prompts]
        all_texts = []
        for sub_batch in chunk_list(prompts, self.batch_size):
            try:
                batch_outputs = self.pipe(sub_batch, candidate_labels=possible_answers,max_new_tokens=self.max_gen_length)
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


class HFLLMModelClassifier(HFLLMModelGenerative):
    """
    Model based on Hugging Face Transformers and pipeline mechanism, loads pretrained LLM models and uses it for inference.
    """

    def __init__(self, model_name, token=None, batch_size=8):
        super().__init__(
            model_name, token, batch_size=batch_size,task="text-generation"
        )

    def infer(self, prompts: str | list[str], possible_answers, conditions=None):
        """Takes a list of prompts as input and uses its loaded model to generate predictions."""
        if not self.loaded:
            self.load_model(self.model_name, task=self.task, token=self.token)
        if isinstance(prompts, str):
            prompts = [prompts]
        all_answers = []
        for sub_batch in chunk_list(prompts, self.batch_size):
            try:

                labels = batch_score_labels(sub_batch,possible_answers,self.model,self.tokenizer)
                all_answers.extend(labels)
            except Exception as e:
                logging.error("error occure",e)
                batch_outputs = [{} for _ in sub_batch]


        return all_answers


def batch_score_labels(
    prompts: list[str],
    candidate_labels: list[str],
    model,
    tokenizer,
):
    device = model.device
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token


    all_scores = []

    for label in candidate_labels:
        label_str = " " + label.strip()
        label_ids = tokenizer(label_str, add_special_tokens=False).input_ids
        label_len = len(label_ids)

        # Build full prompts: prompt + label
        full_prompts = [p.rstrip() + label_str for p in prompts]

        # Tokenize full prompts
        full_inputs = tokenizer(
            full_prompts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=4096,
        ).to(device)

        with torch.no_grad():
            logits = model(**full_inputs).logits  # [batch, seq_len, vocab]
            log_probs = torch.nn.functional.log_softmax(logits, dim=-1)

        batch_scores = []
        for i in range(len(prompts)):
            input_ids = full_inputs.input_ids[i]
            seq_len = input_ids.shape[0]

            # Match label tokens in input_ids using sliding window
            found = False
            for start in range(seq_len - label_len + 1):
                if input_ids[start : start + label_len].tolist() == label_ids:
                    found = True
                    score = sum(
                        log_probs[i, start + j - 1, token_id].item()
                        for j, token_id in enumerate(label_ids)
                    )
                    batch_scores.append(score)
                    break

            if not found:
                batch_scores.append(float("-inf"))

        all_scores.append(batch_scores)

    # [num_labels, batch_size] → [batch_size, num_labels]
    scores_tensor = torch.tensor(all_scores).T  # shape: [batch, labels]
    top_indices = torch.argmax(scores_tensor, dim=1)
    predicted = [candidate_labels[i] for i in top_indices]

    return predicted

# Usage example: