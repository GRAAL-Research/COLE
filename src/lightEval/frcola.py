import os
import huggingface_hub
from datasets import load_dataset
from dotenv import load_dotenv

from lighteval.tasks.lighteval_task import LightevalTaskConfig
from lighteval.tasks.requests import Doc
import lighteval.metrics.metrics as metrics

from src.PromptBuilder import PromptBuilder

load_dotenv()
HF_TOKEN = os.getenv('HF_TOKEN')
huggingface_hub.login(token=HF_TOKEN)

def prompt_fn(line, task_name: str = None):
    prompt = (PromptBuilder()
              .add_premise("Juge si cette phrase est grammaticalement correcte :")
              .add_data(line["sentence"])
              .add_end("Réponds avec seulement 1 si la phrase est grammaticalement correcte, 0 sinon.")
              .build())
    return Doc(
        task_name=task_name,
        query=prompt,
        gold_index=line["label"],
        instruction=""
    )

frcola = LightevalTaskConfig(
    name="frcola",
    prompt_function=prompt_fn,
    hf_repo="COLLE-Graal/ColleGraal",
    hf_subset="data/frcola",
    hf_avail_splits=["train", "validation", "test"],
    evaluation_splits=["test"],
    few_shots_split=None,
    few_shots_select=None,
    metric=[metrics.Metrics.acc_golds_likelihood],
    trust_dataset=True,
)

if __name__ == "__main__":
    dataset = load_dataset(
        path=frcola.hf_repo,
        data_dir=frcola.hf_subset,
        split="test"

    )
    print(dataset)
