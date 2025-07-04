from lighteval.tasks.lighteval_task import LightevalTaskConfig
from lighteval.tasks.requests import Doc

from src import REPO_ID
from src.light_eval_custom.custom_metrics import pearson_metric_wrapper
from src.prompt_builder.prompt_builder import PromptBuilder


def prompt_fn(line, task_name: str = None):
    sent1 = line["sent1"]
    sent2 = line["sent2"]
    prompt = (
        PromptBuilder()
        .add_premise(
            "Les deux phrases suivantes expriment-elles la même idée ou sont-elles différentes ?"
        )
        .add_data(sent1)
        .add_data(sent2)
        .add_end(
            "Réponds seulement avec un chiffre entre 60 et 100 où 100"
            " signifie que les deux phrases veulent dire exactement la même chose."
        )
        .build()
    )
    return Doc(
        task_name=task_name,
        query=prompt,
        gold_index=0,
        choices=[line["quality"]],
        instruction="",
    )


opus_parcus = LightevalTaskConfig(
    name="opus_parcus",
    prompt_function=prompt_fn,
    hf_repo=REPO_ID,
    hf_subset="opus_parcus",
    hf_avail_splits=["test"],
    evaluation_splits=["test"],
    few_shots_split=None,
    few_shots_select=None,
    generation_size=3,
    metric=[pearson_metric_wrapper],
    trust_dataset=True,
)
