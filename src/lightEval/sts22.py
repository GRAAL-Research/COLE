from lighteval.tasks.lighteval_task import LightevalTaskConfig
from lighteval.tasks.requests import Doc
import lighteval.metrics.metrics as metrics
from PromptBuilder import PromptBuilder

REPO_ID = "COLLE-Graal/ColleGraal"


def prompt_fn(line, task_name: str = None):
    """Defines how to go from a dataset line to a doc object.
    Follow examples in src/lighteval/tasks/default_prompts.py, or get more info
    about what this function should do in the README.
    """
    prompt = (PromptBuilder()
              .add_premise("En scorant de 0 à 5, à quel point les phrases suivants sont-elles similaires ?")
              .add_data("sentence 1 :")
              .add_data(line["sentence1"])
              .add_data("sentence 2 :")
              .add_data(line["sentence2"])
              .add_end(
        "Réponds seulement avec un nombre de 0 à 5, où 5 signifie que les 2 phrases veulent dire exactement la même chose. La réponse est :").build())
    return Doc(
        task_name=task_name,
        query=prompt,
        gold_index=int(line["score"]),  # assuming binary classification: 0 or 1
        instruction="",
        choices=[str(i) for i in range(0, 5)],
    )


sts22 = LightevalTaskConfig(
    name="sts22",  # NAME
    prompt_function=prompt_fn,
    # must be defined in the file or imported from src/lighteval/tasks/tasks_prompt_formatting.py
    generation_size=5,
    hf_repo=REPO_ID,
    hf_subset="sts22_crosslingual",
    hf_avail_splits=["test"],
    evaluation_splits=["test"],
    few_shots_split=None,
    few_shots_select=None,
    metric=[metrics.Metrics.pearson_spearman],  # select your metric in Metrics
    trust_dataset=True,
)
