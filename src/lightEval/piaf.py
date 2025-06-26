
from lighteval.tasks.lighteval_task import LightevalTaskConfig
from lighteval.tasks.requests import Doc
import lighteval.metrics.metrics as metrics
from src.PromptBuilder import PromptBuilder

REPO_ID = "COLLE-Graal/ColleGraal"



def prompt_fn(line, task_name: str = None):
    """Defines how to go from a dataset line to a doc object.
    Follow examples in src/lighteval/tasks/default_prompts.py, or get more info
    about what this function should do in the README.
    """
    gold = line["answers"]["answer_start"][0]
    context = line["context"]
    question = line["question"]
    prompt = (PromptBuilder()
    .add_premise(
        "Voici une question et un contexte. Où, dans le texte, commence la réponse à la question ?")
    .add_data(f"Contexte : {context}")
    .add_data(f"Question : {question}")
    .add_end(
        "Réponds seulement avec le nombre de charactères qui précèdent la réponse à la question dans le contexte. La réponse est :").build())
    return Doc(
        task_name=task_name,
        query=prompt,
        gold_index=0,  # assuming binary classification: 0 or 1
        instruction="",
        choices = [gold],
    )
piaf = LightevalTaskConfig(
    name="piaf", #NAME
    prompt_function=prompt_fn,  # must be defined in the file or imported from src/lighteval/tasks/tasks_prompt_formatting.py
    generation_size=5,
    hf_repo=REPO_ID,
    hf_subset="piaf",
    hf_avail_splits=["train", "validation", "test"],
    evaluation_splits=["test"],
    few_shots_split=None,
    few_shots_select=None,
    metric=[metrics.Metrics.pearson_spearman],  # select your metric in Metrics
    trust_dataset=True,
)