import os

import huggingface_hub
from datasets import load_dataset
from dotenv import load_dotenv
import src.lightEval.pearsonAndSpearman
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
    context = line["context"]
    question = line["question"]
    prompt = (PromptBuilder()
    .add_premise(
        "Voici une question et un contexte. Où, dans le texte, commence la réponse à la question ?")
    .add_data(f"Question : {question}")
    .add_data(f"Contexte : {context}")
    .add_end(
        "Réponds seulement avec le **nombre de mots** qui précèdent la réponse à la question dans le contexte.").build())
    return Doc(
        task_name=task_name,
        query=prompt,
        gold_index=line["answers"]["answer_start"][0],  # assuming binary classification: 0 or 1
        instruction=""
    )
piaf = LightevalTaskConfig(
    name="piaf", #NAME
    prompt_function=prompt_fn,  # must be defined in the file or imported from src/lighteval/tasks/tasks_prompt_formatting.py

    hf_repo=REPO_ID,
    hf_subset="data/piaf",
    hf_avail_splits=["train", "validation", "test"],
    evaluation_splits=["test"],
    few_shots_split=None,
    few_shots_select=None,
    metric=[metrics.Metrics.pearson_spearman],  # select your metric in Metrics
    trust_dataset=True,
)