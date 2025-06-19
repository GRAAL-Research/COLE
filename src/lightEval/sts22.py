import os

import huggingface_hub
from datasets import load_dataset
from dotenv import load_dotenv

from lighteval.tasks.lighteval_task import LightevalTaskConfig
from lighteval.tasks.requests import Doc
import lighteval.metrics.metrics as metrics
from src.PromptBuilder import PromptBuilder

REPO_ID = "COLLE-Graal/ColleGraal"

load_dotenv()
HF_TOKEN = os.getenv('HF_TOKEN')
print(HF_TOKEN)
huggingface_hub.login(token=HF_TOKEN)

def prompt_fn(line, task_name: str = None):
    """Defines how to go from a dataset line to a doc object.
    Follow examples in src/lighteval/tasks/default_prompts.py, or get more info
    about what this function should do in the README.
    """
    prompt = (PromptBuilder()
    .add_premise("En scorant de 0 à 5, à quel point les phrases suivants sont-elles similaires ?")
    .add_data(line["sentence1"])
    .add_data(line["sentence2"])
    .add_end(
        "Réponds seulement avec un nombre de 0 à 5, où 5 signifie que les 2 phrases veulent dire exactement la même chose.").build())
    return Doc(
        task_name=task_name,
        query=prompt,
        gold_index=float(line["score"]),  # assuming binary classification: 0 or 1
        instruction=""
    )
sts22 = LightevalTaskConfig(
    name="sts22", #NAME
    prompt_function=prompt_fn,  # must be defined in the file or imported from src/lighteval/tasks/tasks_prompt_formatting.py

    hf_repo=REPO_ID,
    hf_subset="data/sts22",
    hf_avail_splits=["train", "dev", "test"],
    evaluation_splits=["test"],
    few_shots_split=None,
    few_shots_select=None,
    metric=[metrics.Metrics.acc_golds_likelihood],  # select your metric in Metrics
    trust_dataset=True,
)