import os

import lighteval
from lighteval.logging.evaluation_tracker import EvaluationTracker
from lighteval.models.transformers.transformers_model import TransformersModelConfig
from lighteval.pipeline import ParallelismManager, Pipeline, PipelineParameters
from lighteval.utils.imports import is_accelerate_available
import CustomMetrics
if is_accelerate_available():
    from datetime import timedelta
    from accelerate import Accelerator, InitProcessGroupKwargs

    accelerator = Accelerator(kwargs_handlers=[InitProcessGroupKwargs(timeout=timedelta(seconds=3000))])
else:
    accelerator = None


def main():

    print("Searching for custom tasks in:", os.path.abspath("./"))

    def build_pipeline(model_name):
        evaluation_tracker = EvaluationTracker(
            output_dir="./results",
            save_details=True,
            push_to_hub=False,
        )
        pipeline_params = PipelineParameters(
            launcher_type=ParallelismManager.ACCELERATE,
            custom_tasks_directory="./tasks.py",
            # Remove the 2 parameters below once your configuration is tested
            max_samples=3,

        )

        tasks = build_tasks_name()
        return Pipeline(
            tasks=tasks,
            pipeline_parameters=pipeline_params,
            evaluation_tracker=evaluation_tracker,
            model_config=build_config(model_name),
        )
    pipeline = build_pipeline("babylm/babyllama100m-2024")
    pipeline.model_config = build_config("distilbert-base-uncased-finetuned-sst-2-english")
    pipeline.evaluate()
    pipeline.save_and_push_results()
    pipeline.show_results()

    pipeline = build_pipeline("distilbert-base-uncased-finetuned-sst-2-english")
    pipeline.evaluate()

def build_tasks_name():
    tasks_names = ["allocine", "paws_x", "fquad", "opus_parcus", "gqnli", "piaf", "sickfr", "xnli", "frcola", "frblimp",
                   "sts22"]
    tasks = [build_task(name=task_name) for task_name in tasks_names]
    return ",".join(tasks)


def build_task(section="custom", name=None, shots=0, instruct=0):
    return f"{section}|{name}|{shots}|{instruct}"

def build_config(model_name):
    return TransformersModelConfig(
        model_name=model_name,
        dtype="auto",
        use_chat_template=True,
        device="cuda",
        batch_size=2
    )

if __name__ == "__main__":
    main()
