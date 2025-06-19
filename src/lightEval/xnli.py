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
              .add_premise("Quelle est la relation de la deuxième phrase par rapport à la première ?")
              .add_data(line["premise"]).add_data(line["hypothesis"])
              .add_end("Réponds uniquement par :\n"
                       "0 — si la deuxième phrase implique la première,\n"
                       "1 — si la relation est neutre,\n"
                       "2 — s'il y a contradiction.\n"
                       "Réponds uniquement par 0, 1 ou 2.")
              .build())
    return Doc(
        task_name=task_name,
        query=prompt,
        gold_index=line["label"],
        choices=["0", "1", "2"],
        instruction=""
    )
xnli = LightevalTaskConfig(
    name="xnli", #NAME
    prompt_function=prompt_fn,  # must be defined in the file or imported from src/lighteval/tasks/tasks_prompt_formatting.py

    hf_repo=REPO_ID,
    hf_subset="data/xnli",
    hf_avail_splits=["train", "dev", "test"],
    evaluation_splits=["test"],
    few_shots_split=None,
    few_shots_select=None,
    metric=[metrics.Metrics.acc_golds_likelihood],  # select your metric in Metrics
    trust_dataset=True,
)