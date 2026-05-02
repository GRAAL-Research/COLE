import argparse
from typing import List, Union


def split_llm_list(models: List, llm_split: Union[None, int]) -> List:
    if llm_split is None:
        return models
    if llm_split not in (1, 2, 3):
        raise ValueError("llm_split must be in [1, 2, 3].")
    if llm_split == 1:
        models = models[: len(models) // 3]
    elif llm_split == 2:
        models = models[len(models) // 3 : 2 * len(models) // 3]
    elif llm_split == 3:
        models = models[2 * len(models) // 3 :]
    return models


def str2bool(value: Union[bool, str]) -> bool:
    """argparse-friendly bool parser.

    `argparse(type=bool)` is a footgun: `bool("False")` is True, so any
    non-empty string flips the flag to True. This converter rejects garbage
    explicitly and accepts the obvious truthy/falsy spellings.
    """
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in ("true", "1", "yes", "y", "t"):
        return True
    if normalized in ("false", "0", "no", "n", "f"):
        return False
    raise argparse.ArgumentTypeError(f"Boolean value expected, got: {value!r}")
