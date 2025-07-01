import lighteval.metrics.metrics as metrics
from lighteval.tasks.lighteval_task import LightevalTaskConfig
from lighteval.tasks.requests import Doc

from src.prompt_builder.prompt_builder import PromptBuilder
from src.tasks_custom import REPO_ID


def prompt_fn(line, task_name: str = None):
    sentence1 = line["sentence1"]
    sentence2 = line["sentence2"]
    prompt = (
        PromptBuilder()
        .add_premise(
            "Les deux phrases suivantes veulent-elles dire la même chose, ou ont-elles des significations différentes ?"
        )
        .add_data(sentence1)
        .add_data(sentence2)
        .add_end(
            "Réponds seulement 1 si les deux phrases ont la même signification, 0 sinon. La réponse est :"
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


paws_x = LightevalTaskConfig(
    name="paws_x",
    prompt_function=prompt_fn,
    hf_repo=REPO_ID,
    hf_subset="paws_x",
    hf_avail_splits=["train", "validation", "test"],
    evaluation_splits=["test"],
    few_shots_split=None,
    few_shots_select=None,
    metric=[metrics.Metrics.accuracy_wrapper],
    trust_dataset=True,
)
