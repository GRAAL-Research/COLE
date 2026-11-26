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


def select_tasks(
    group_task_names: List[str], requested_tasks: Union[None, str]
) -> List[str]:
    """Restrict a task group to a comma-separated selection.

    Args:
        group_task_names: Names of the tasks of the selected group.
        requested_tasks: Comma-separated task names, or None/empty to keep the whole group.

    Returns:
        The selected task names, in the order of the group (duplicates removed).

    Raises:
        ValueError: If a requested task is not part of the group.
    """
    if requested_tasks is None or not requested_tasks.strip():
        return list(group_task_names)
    requested = [name.strip() for name in requested_tasks.split(",") if name.strip()]
    unknown = [name for name in requested if name not in group_task_names]
    if unknown:
        raise ValueError(
            f"Unknown task(s) for this group: {', '.join(unknown)}. "
            f"Available: {', '.join(group_task_names)}."
        )
    return [name for name in group_task_names if name in requested]
