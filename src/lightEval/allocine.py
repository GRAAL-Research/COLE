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
              .add_premise("Cette phrase possède-t-elle un sentiment positif ou négatif ?")
              .add_data(line["review"])
              .add_end(("Réponds "
                        "uniquement par 1 si la phrase est positive,réponds par 0 sinon. La réponse est : ")).build()
              )
    return Doc(
        task_name=task_name,
        query=prompt,
        gold_index=line["label"],
        choices=["0", "1"],

        instruction=""
    )


allocine = LightevalTaskConfig(
    name="allocine", #NAME
    prompt_function=prompt_fn,  # must be defined in the file or imported from src/lighteval/tasks/tasks_prompt_formatting.py

    hf_repo=REPO_ID,
    hf_subset="allocine",
    hf_avail_splits=["train", "validation", "test"],
    evaluation_splits=["test"],
    few_shots_split=None,
    few_shots_select=None,
    metric=[metrics.Metrics.accuracy_wrapper],  # select your metric in Metrics
    trust_dataset=True,
)

