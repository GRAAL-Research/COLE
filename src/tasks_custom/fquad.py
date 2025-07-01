import lighteval.metrics.metrics as metrics
from lighteval.tasks.lighteval_task import LightevalTaskConfig
from lighteval.tasks.requests import Doc

from src.prompt_builder.prompt_builder import PromptBuilder
from src.tasks_custom import REPO_ID


def prompt_fn(line, task_name: str = None):
    prompt = (
        PromptBuilder()
        .add_premise(
            "Voici un contexte et une question. Réponds à la question en te basant uniquement sur le contexte."
        )
        .add_data("contexte : ")
        .add_data(line["context"])
        .add_data("question :")
        .add_data(line["question"])
        .add_end(
            "Dans le texte ci-dessous, combien de caractères précèdent la réponse à la question ? Réponds uniquement avec un nombre.. La réponse est : "
        )
        .build()
    )
    is_impossible = line["is_impossible"]
    answers = [str(i) for i in line["answers"]["answers_start"]]
    return Doc(
        task_name=task_name,
        query=prompt,
        gold_index=0,
        instruction="",
        choices=answers if not is_impossible else ["0"],
    )


fquad = LightevalTaskConfig(
    name="fquad",
    prompt_function=prompt_fn,
    generation_size=5,
    hf_repo=REPO_ID,
    hf_subset="fquad",
    hf_avail_splits=["test"],
    evaluation_splits=["test"],
    few_shots_split=None,
    few_shots_select=None,
    metric=[metrics.Metrics.pearson_spearman],
    trust_dataset=True,
)
