import lighteval.metrics.metrics as metrics
from lighteval.tasks.lighteval_task import LightevalTaskConfig
from lighteval.tasks.requests import Doc

from src import REPO_ID
from src.light_eval_custom.custom_metrics import accuracy_wrapper
from src.prompt_builder.prompt_builder import PromptBuilder


def prompt_fn(line, task_name: str = None):
    """Defines how to go from a dataset line to a doc object.
    Follow examples in src/lighteval/tasks/default_prompts.py, or get more info
    about what this function should do in the README.
    """
    prompt = (
        PromptBuilder()
        .add_premise("Cette phrase possède-t-elle un sentiment positif ou négatif ?")
        .add_data(line["review"])
        .add_end(
            (
                "Réponds "
                "uniquement par 1 si la phrase est positive,réponds par 0 sinon. La réponse est : "
            )
        )
        .build()
    )
    return Doc(
        task_name=task_name,
        query=prompt,
        gold_index=line["label"],
        choices=["0", "1"],
        instruction="",
    )


allocine = LightevalTaskConfig(
    name="allocine",
    prompt_function=prompt_fn,
    hf_repo=REPO_ID,
    hf_subset="allocine",
    hf_avail_splits=["train", "validation", "test"],
    evaluation_splits=["test"],
    few_shots_split=None,
    few_shots_select=None,
    metric=[accuracy_wrapper],
    trust_dataset=True,
)
