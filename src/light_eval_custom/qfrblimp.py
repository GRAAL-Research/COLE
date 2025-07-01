from lighteval.tasks.lighteval_task import LightevalTaskConfig
from lighteval.tasks.requests import Doc
import lighteval.metrics.metrics as metrics
from prompt_builder import PromptBuilder

REPO_ID = "COLLE-Graal/ColleGraal"

seed = 32144523


def get_0_1_seeded(test):
    return (seed + test["__index"] ^ 2 * 7) % 2


def prompt_fn(line, task_name: str = None):
    if get_0_1_seeded(line) == 1:
        data = line["grammatical"]
    else:
        data = line["ungrammatical"]
    prompt = (
        PromptBuilder()
        .add_premise("Cette phrase est-elle grammaticalement correcte ?")
        .add_data(data)
        .add_end(
            "Réponds strictement par 1 si la phrase est correcte grammaticalement ; sinon, réponds 0."
        )
        .build()
    )
    return Doc(
        task_name=task_name,
        query=prompt,
        gold_index=get_0_1_seeded(line),
        choices=["0", "1"],
        instruction="",
    )


frblimp = LightevalTaskConfig(
    name="frblimp",
    prompt_function=prompt_fn,
    hf_repo=REPO_ID,
    hf_subset="fr_blimp",
    hf_avail_splits=["train", "validation", "test"],
    evaluation_splits=["test"],
    few_shots_split=None,
    few_shots_select=None,
    metric=[metrics.Metrics.accuracy_wrapper],
    trust_dataset=True,
)
