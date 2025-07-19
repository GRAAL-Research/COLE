from typing import Callable, Any, Union
from datasets import load_dataset


class Dataset:
    """Class representing a usable dataset.
    Allows dataset to be expressed as multiple forms, including as prompts, data or answers.
    :param name : name of the dataset.
    :param description : description of the dataset.
    :param possible_ground_truths : the form that could be taken by ground truths.
    :param hugging_face_repo : where to download the dataset on HuggingFace.
    :param line_to_truth_fn : a function converting a dataset line to its truth value.
    :param line_to_prompt_fn : a function converting a dataset line to a prompt for LLM inference.
    :param line_to_data_fn : a function converting a dataset line to its data value for non LLM inference.
    """

    def __init__(
        self,
        name: str,
        description: str,
        possible_ground_truths: Union[list[str], list[int], list[float]],
        hugging_face_repo: str,
        line_to_truth_fn: Callable,
        line_to_prompt_fn: Callable,
        line_to_data_fn: Callable,
    ):
        self._dataset = None
        self.name = name
        self.description = description
        self.hugging_face_repo = hugging_face_repo
        self.possible_ground_truths = possible_ground_truths
        self.line_to_prompt_fn = line_to_prompt_fn
        self.line_to_truth_fn = line_to_truth_fn
        self.line_to_data_fn = line_to_data_fn

    @property
    def dataset(self):
        self.load_data()
        return self._dataset

    def load_data(self):
        if self._dataset is None:
            self._dataset = load_dataset(
                self.hugging_face_repo, name=self.name, split="test"
            )

    @property
    def ground_truths(self) -> Union[list[str], list[int], list[float]]:
        """The dataset's ground truths as a list"""
        return [self.line_to_truth_fn(line) for line in self.dataset]

    @property
    def prompts(self) -> list[str]:
        """The dataset's prompts as a list"""
        return [self.line_to_prompt_fn(line) for line in self.dataset]

    @property
    def data(self) -> list[str]:
        """The dataset's data as a list"""
        return [self.line_to_data_fn(line) for line in self.dataset]

    @property
    def metadata(self) -> dict[str, Any]:
        """The dataset's metadata as a dict"""
        return {
            "description": self.description,
            "possible_ground_truths": str(self.possible_ground_truths),
        }
