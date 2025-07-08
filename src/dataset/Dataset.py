from datasets import load_dataset
from src.task import REPOSITORY_NAME
from predictions.utils import hugging_face_login

hugging_face_login("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")


class Dataset:
    def __init__(
        self,
        name,
        huggingFace_repo,
        line_to_thruth_fn,
        line_to_prompt_fn,
        line_to_data_fn,
    ):
        self.data = load_dataset(f"{huggingFace_repo}", name=name, split="test")
        self.line_to_prompt_fn = line_to_prompt_fn
        self.line_to_thruth_fn = line_to_thruth_fn
        self.line_to_data_fn = line_to_data_fn

    @property
    def ground_truths(self):
        return [self.line_to_thruth_fn(line) for line in self.data]

    @property
    def prompts(self):
        return [self.line_to_prompt_fn(line) for line in self.data]

    @property
    def data(self):
        return [self.line_to_data_fn(line) for line in self.data]
