from lighteval.tasks.lighteval_task import LightevalTaskConfig
from lighteval.tasks.requests import Doc

from src import REPO_ID
from src.light_eval_custom.custom_metrics import accuracy_wrapper
from src.prompt_builder.prompt_builder import PromptBuilder


def prompt_fn(line, task_name: str = None):
    prompt = (
        PromptBuilder()
        .add_premise(
            "Quelle est la relation de la deuxième phrase par rapport à la première ?"
        )
        .add_data(line["premise"])
        .add_data(line["hypothesis"])
        .add_end(
            "Réponds uniquement par :\n"
            "0 — si la deuxième phrase implique la première,\n"
            "1 — si la relation est neutre,\n"
            "2 — s'il y a contradiction.\n"
            "Réponds uniquement par 0, 1 ou 2."
        )
        .build()
    )
    return Doc(
        task_name=task_name,
        query=prompt,
        gold_index=line["label"],
        choices=["0", "1", "2"],
        instruction="",
    )


gqnli = LightevalTaskConfig(
    name="gqnli",
    prompt_function=prompt_fn,
    hf_repo=REPO_ID,
    hf_subset="gqnli",
    hf_avail_splits=["train", "validation", "test"],
    evaluation_splits=["test"],
    few_shots_split=None,
    few_shots_select=None,
    metric=[accuracy_wrapper],
    trust_dataset=True,
)
TASKS_TABLE = [gqnli]
