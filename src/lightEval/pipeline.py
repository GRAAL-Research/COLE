import os

import huggingface_hub
import lighteval
from lighteval.logging.evaluation_tracker import EvaluationTracker
from lighteval.models.vllm.vllm_model import VLLMModelConfig
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

    pipeline_params = PipelineParameters(
        launcher_type=ParallelismManager.ACCELERATE,
        custom_tasks_directory="./",
        # Remove the 2 parameters below once your configuration is tested
        max_samples=10
    )

    model_config = VLLMModelConfig(
            model_name="babylm/babyllama-100m-2024",
            dtype="float16",
            use_chat_template=True,
    )

    task = "lighteval|frcola|0|0"

    pipeline = Pipeline(
        tasks=task,
        pipeline_parameters=pipeline_params,
        evaluation_tracker=evaluation_tracker,
        model_config=model_config,
    )

    pipeline.evaluate()
    pipeline.save_and_push_results()
    pipeline.show_results()

if __name__ == "__main__":
    main()