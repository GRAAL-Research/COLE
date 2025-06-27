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
    sent1 = line["sent1"]
    sent2 = line["sent2"]
    prompt = (PromptBuilder()
              .add_premise("Les deux phrases suivantes expriment-elles la même idée ou sont-elles différentes ?")
              .add_data(sent1).add_data(sent2)
              .add_end("Réponds seulement avec un chiffre entre 60 et 100 où 100"
                       " signifie que les deux phrases veulent dire exactement la même chose.").build())
    return Doc(
        task_name=task_name,
        query=prompt,
        gold_index=0,
        choices=[line["quality"]],
        instruction=""
    )
opus_parcus = LightevalTaskConfig(
    name="opus_parcus", #NAME
    prompt_function=prompt_fn,  # must be defined in the file or imported from src/lighteval/tasks/tasks_prompt_formatting.py
    hf_repo=REPO_ID,
    hf_subset="opus_parcus",
    hf_avail_splits=["test"],
    evaluation_splits=["test"],
    few_shots_split=None,
    few_shots_select=None,
    metric=[metrics.Metrics.pearson_spearman],

    trust_dataset=True,
)
print(metrics.Metrics.pearson_spearman)