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

load_dotenv()
HF_TOKEN = os.getenv('HF_TOKEN')
print(HF_TOKEN)
huggingface_hub.login(token=HF_TOKEN)

def prompt_fn(line, task_name: str = None):
    """Defines how to go from a dataset line to a doc object.
    Follow examples in src/lighteval/tasks/default_prompts.py, or get more info
    about what this function should do in the README.
    """
    #TODO build fquad prompt
    prompt = (PromptBuilder()
              .add_premise("")
              .add_data()
              .add_end("").build())
    is_impossible = line["is_impossible"]
    return Doc(
        task_name=task_name,
        query=prompt,
        gold_index= 1 if not is_impossible else 0,  # assuming binary classification: 0 or 1
        instruction=""
    )
fquad = LightevalTaskConfig(
    name="fquad", #NAME
    prompt_function=prompt_fn,  # must be defined in the file or imported from src/lighteval/tasks/tasks_prompt_formatting.py

    hf_repo=REPO_ID,
    hf_subset="data/fquad",
    hf_avail_splits=["train", "validation", "test"],
    evaluation_splits=["test"],
    few_shots_split=None,
    few_shots_select=None,
    metric=[metrics.Metrics.pearson_spearman],  # select your metric in Metrics
    trust_dataset=True,
)