import os

from lighteval.logging.evaluation_tracker import EvaluationTracker
from lighteval.models.transformers.transformers_model import TransformersModelConfig
from lighteval.models.vllm.vllm_model import VLLMModelConfig
from lighteval.pipeline import ParallelismManager, Pipeline, PipelineParameters
from lighteval.utils.imports import is_accelerate_available
import lightEval.Utils as Utils
#import custom components
import CustomMetrics
import tasks

if is_accelerate_available():
    from datetime import timedelta
    from accelerate import Accelerator, InitProcessGroupKwargs

    accelerator = Accelerator(kwargs_handlers=[InitProcessGroupKwargs(timeout=timedelta(seconds=3000))])
else:
    accelerator = None

def main():

    print("Searching for custom tasks in:", os.path.abspath("./"))


    pipeline = build_pipeline("distilbert/distilgpt2")
    pipeline.evaluate()
    pipeline.save_and_push_results()
    pipeline.show_results()

    pipeline = build_pipeline("EleutherAI/pythia-70m")
    pipeline.evaluate()
    pipeline.save_and_push_results()
    pipeline.show_results()


def build_tasks_name():
    #tasks_names = ["allocine", "paws_x", "fquad", "opus_parcus", "gqnli", "piaf", "sickfr", "xnli", "frcola", "frblimp","sts22"]
    tasks_names = [ "fquad"]
    tasks = [build_task(name=task_name) for task_name in tasks_names]
    return ",".join(tasks)


def build_task(section="custom", name=None, shots=0, instruct=0):
    return f"{section}|{name}|{shots}|{instruct}"

def build_transformers_config(model_name):
    return TransformersModelConfig(
        model_name=model_name,
        dtype="auto",
        use_chat_template=True,
        device="cuda",
        batch_size=4,
        max_length= 5

    )
def build_vllm_config(model_name):
    return VLLMModelConfig(
        model_name=model_name,
        dtype="auto",
        use_chat_template=True,
        gpu_memory_utilization=0.8,
    )
def create_model_config(model_name):
    print("creating model config.")
    try:
        return build_vllm_config(model_name)
    except Exception as e:
        print("Could not create model as VLLM, falling back to transformers...")
        return build_transformers_config(model_name)

def build_pipeline(model_name,max = None):
    evaluation_tracker = EvaluationTracker(
        output_dir="./results",
        save_details=False,
        push_to_hub=False,
    )
    pipeline_params = PipelineParameters(
        launcher_type=ParallelismManager.ACCELERATE,
        custom_tasks_directory="./tasks.py",
        # Remove the 2 parameters below once your configuration is tested
        max_samples=max,

        )

    tasks = build_tasks_name()
    return Pipeline(
        tasks=tasks,
        pipeline_parameters=pipeline_params,
        evaluation_tracker=evaluation_tracker,
        model_config=build_vllm_config(model_name),
        )

def test_model(model_name, max_samples = None):
    pipeline = build_pipeline(model_name, max_samples)
    pipeline.evaluate()
    pipeline.save_and_push_results()
    pipeline.show_results()

if __name__ == "__main__":
    Utils.hugging_face_login()
    test_model("EleutherAI/pythia-70m", max_samples=10000)
