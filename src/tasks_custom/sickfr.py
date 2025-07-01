import lighteval.metrics.metrics as metrics
from lighteval.tasks.lighteval_task import LightevalTaskConfig
from lighteval.tasks.requests import Doc

from src.prompt_builder.prompt_builder import PromptBuilder
from src.tasks_custom import REPO_ID


def prompt_fn(line, task_name: str = None):
    sentence_A = line["sentence_A"]
    sentence_B = line["sentence_B"]
    prompt = (
        PromptBuilder()
        .add_premise(
            "À quel point, de 0 à 5, les 2 phrases suivantes sont-elles similaires ?"
        )
        .add_data(sentence_A)
        .add_data(sentence_B)
        .add_end(
            "Réponds avec seulement un nombre de 0 à 5, où 5 signifie une très grande similarité entre les phrases."
        )
        .build()
    )
    return Doc(
        task_name=task_name,
        query=prompt,
        gold_index=0,
        choices=[line["relatedness_score"]],
        instruction="",
    )


sickfr = LightevalTaskConfig(
    name="sickfr",
    prompt_function=prompt_fn,
    generation_size=5,
    hf_repo=REPO_ID,
    hf_subset="sickfr",
    hf_avail_splits=["train", "validation", "test"],
    evaluation_splits=["test"],
    few_shots_split=None,
    few_shots_select=None,
    metric=[metrics.Metrics.pearson_spearman],
    trust_dataset=True,
)
