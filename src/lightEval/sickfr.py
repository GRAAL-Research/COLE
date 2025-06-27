import os
import huggingface_hub
from dotenv import load_dotenv
from lighteval.tasks.lighteval_task import LightevalTaskConfig
from lighteval.tasks.requests import Doc
import lighteval.metrics.metrics as metrics
from PromptBuilder import PromptBuilder

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
    sentence_A = line["sentence_A"]
    sentence_B = line["sentence_B"]
    prompt = (PromptBuilder()
              .add_premise("À quel point, de 0 à 5, les 2 phrases suivantes sont-elles similaires ?")
              .add_data(sentence_A).add_data(sentence_B)
              .add_end(
        "Réponds avec seulement un nombre de 0 à 5, où 5 signifie une très grande similarité entre les phrases.").build())
    return Doc(
        task_name=task_name,
        query=prompt,
        gold_index=0,
        choices=[line["relatedness_score"]],
        instruction=""
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
    metric=[metrics.Metrics.pearson_spearman],  # select your metric in Metrics
    trust_dataset=True,
)
