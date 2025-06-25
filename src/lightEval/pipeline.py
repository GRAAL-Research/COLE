import os

import huggingface_hub
import lighteval
from datasets import load_dataset

import CustomMetrics
from lighteval.logging.evaluation_tracker import EvaluationTracker
from lighteval.models.transformers.transformers_model import TransformersModelConfig
from lighteval.pipeline import ParallelismManager, Pipeline, PipelineParameters
from lighteval.utils.imports import is_accelerate_available
from dotenv import load_dotenv


load_dotenv()
REPO_ID = "COLLE-Graal/ColleGraal"
HF_TOKEN = os.getenv('HF_TOKEN')

huggingface_hub.login(token=HF_TOKEN)

if is_accelerate_available():
    from datetime import timedelta
    from accelerate import Accelerator, InitProcessGroupKwargs
    accelerator = Accelerator(kwargs_handlers=[InitProcessGroupKwargs(timeout=timedelta(seconds=3000))])
else:
    accelerator = None

def main():
    evaluation_tracker = EvaluationTracker(
        output_dir="./results",
        save_details=True,
        push_to_hub=False,
    )
    print("Searching for custom tasks in:", os.path.abspath("./"))
    pipeline_params = PipelineParameters(
        launcher_type=ParallelismManager.ACCELERATE,
        custom_tasks_directory="./tasks.py",
        # Remove the 2 parameters below once your configuration is tested
        max_samples=3,

    )
    print(lighteval.pipeline.Registry)
    model_config = TransformersModelConfig(
            model_name="mistralai/Mistral-7B-v0.1",
            dtype="auto",
            use_chat_template=True,
            device="cuda",
            batch_size=1
    )

    task = build_tasks_name()
    print(task)
    pipeline = Pipeline(
        tasks=task,
        pipeline_parameters=pipeline_params,
        evaluation_tracker=evaluation_tracker,
        model_config=model_config,


    )

    pipeline.evaluate()
    print("task dict :",pipeline.task_dict)
    print("results : ", pipeline.get_results())
    pipeline.save_and_push_results()
    pipeline.show_results()

def build_tasks_name ():
    tasks_names = ["allocine", "paws_x", "fquad", "opus_parcus", "gqnli", "piaf", "sickfr", "xnli","frcola","frblimp","sts22"]
    tasks = [build_task(name=task_name) for task_name in tasks_names]
    return ",".join(tasks)
def build_task(section="custom",name=None,shots=0,instruct=0):
    return f"{section}|{name}|{shots}|{instruct}"
if __name__ == "__main__":
    main()
