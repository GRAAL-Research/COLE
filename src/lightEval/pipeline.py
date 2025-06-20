import os

import huggingface_hub
import lighteval

from lighteval.logging.evaluation_tracker import EvaluationTracker
from lighteval.models.transformers.transformers_model import TransformersModelConfig
from lighteval.pipeline import ParallelismManager, Pipeline, PipelineParameters
from lighteval.utils.imports import is_accelerate_available
from dotenv import load_dotenv


load_dotenv()
REPO_ID = "COLLE-Graal/ColleGraal"
HF_TOKEN = os.getenv('HF_TOKEN')
print(HF_TOKEN)
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
        #max_samples=10,

    )
    print(lighteval.pipeline.Registry)
    model_config = TransformersModelConfig(
            model_name="babylm/babyllama-100m-2024",
            dtype="float16",
            use_chat_template=True,
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
    print(pipeline.task_dict)
    print(pipeline.get_results())
    pipeline.save_and_push_results()
    pipeline.show_results()

def build_tasks_name ():
    tasks = ["custom|frcola|0|0",]
    return ",".join(tasks)

if __name__ == "__main__":
    main()
