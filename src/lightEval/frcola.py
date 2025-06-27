from lighteval.metrics.metrics import Metrics
from lighteval.tasks.lighteval_task import LightevalTaskConfig
from lighteval.tasks.requests import Doc
from src.lightEval.PromptBuilder import PromptBuilder

print("using local frcola")


def prompt_fn(line, task_name: str = None):
    prompt = (PromptBuilder()
              .add_premise("Juge si cette phrase est grammaticalement correcte :")
              .add_data(line["sentence"])
              .add_end(
        "Réponds avec seulement 1 si la phrase est grammaticalement correcte, 0 sinon. La réponse est : ")
              .build())
    return Doc(
        task_name=task_name,
        query=prompt,
        gold_index=line["label"],
        choices=["0", "1"],
    )


frcola = LightevalTaskConfig(
    name="frcola",
    prompt_function=prompt_fn,
    suite=["custom"],
    hf_repo="COLLE-Graal/ColleGraal",
    hf_subset="frcola",
    hf_avail_splits=["train", "validation", "test"],
    evaluation_splits=["test"],
    few_shots_split=None,
    few_shots_select=None,
    metric=[Metrics.accuracy_wrapper],
    trust_dataset=True,
    stop_sequence=[],
)

TASKS_TABLE = [frcola]
