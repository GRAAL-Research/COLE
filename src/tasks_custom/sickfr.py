from lighteval.tasks.lighteval_task import LightevalTaskConfig
from lighteval.tasks.requests import Doc

from src import REPO_ID
from src.light_eval_custom.custom_metrics import pearson_metric_wrapper
from src.prompt_builder.prompt_builder import PromptBuilder


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
            "Réponds avec seulement un nombre de 0 à 5, où 5 signifie une très grande similarité entre les phrases. La réponse est :"
        )
        .build()
    )

    rounded_relatedness = round(line["relatedness_score"] * 2) / 2
    choices = [str(i * 0.5) for i in range(0, 11)]
    gold_index = choices.index(str(rounded_relatedness))
    return Doc(
        task_name=task_name,
        query=prompt,
        gold_index=gold_index,
        choices=choices,
        instruction="",
    )


sickfr = LightevalTaskConfig(
    name="sickfr",
    prompt_function=prompt_fn,
    generation_size=5,
    hf_repo=REPO_ID,
    hf_subset="sickfr",
    hf_avail_splits=["test"],
    evaluation_splits=["test"],
    few_shots_split=None,
    few_shots_select=None,
    metric=[pearson_metric_wrapper],
    trust_dataset=True,
)
