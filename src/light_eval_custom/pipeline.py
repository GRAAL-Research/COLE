from lighteval.logging.evaluation_tracker import EvaluationTracker
from lighteval.models.transformers.transformers_model import TransformersModelConfig
from lighteval.models.vllm.vllm_model import VLLMModelConfig
from lighteval.pipeline import ParallelismManager, Pipeline, PipelineParameters
from lighteval.utils.imports import is_accelerate_available

from src.light_eval_custom.custom_metrics import add_custom_metrics_to_lighteval



CUSTOM_TASKS_DIRECTORY = "./src/light_eval_custom/custom_tasks.py"
add_custom_metrics_to_lighteval()

if is_accelerate_available():
    from datetime import timedelta
    from accelerate import Accelerator, InitProcessGroupKwargs

    accelerator = Accelerator(
        kwargs_handlers=[InitProcessGroupKwargs(timeout=timedelta(seconds=3000))]
    )
else:
    accelerator = None

class PipelineConfig:
    def __init__(self,backend="vllm",batch_size=8,max_length=2048):
        self.backend = backend
        self.batch_size = batch_size
        self.max_length = max_length

def build_tasks_name():
    tasks_names = [
        "allocine",
        "paws_x",
        "fquad",
        "opus_parcus",
        "gqnli",
        "piaf",
        "sickfr",
        "xnli",
        "qfrcola",
        "qfrblimp",
        "sts22",
    ]
    tasks = [build_task(name=task_name) for task_name in tasks_names]
    return ",".join(tasks)


def build_task(section="custom", name=None, shots=0, instruct=0):
    return f"{section}|{name}|{shots}|{instruct}"


def create_model_config(model_name, config : PipelineConfig):
    try:
        if config.backend == "transformers":
            return build_transformers_config(model_name,config)
        elif config.backend == "vllm":
            return build_vllm_config(model_name,config)
        else:
            print(f"backend configuration {config.backend} unavailable, defaulting to vllm")
            return build_vllm_config(model_name,config)

    except Exception as e:
        print("Could not create model, falling back to transformers...")
        return build_transformers_config(model_name)


def build_transformers_config(model_name,config):
    return TransformersModelConfig(
        model_name=model_name,
        dtype="auto",
        use_chat_template=True,
        device="cuda",
        batch_size=config.batch_size,
        max_length=config.max_length,
    )


def build_vllm_config(model_name,config):
    return VLLMModelConfig(
        model_name=model_name,
        dtype="auto",
        use_chat_template=True,
        gpu_memory_utilization=0.8,
    )


def build_pipeline(
    model_name,
    max_samples,
    config : PipelineConfig,
):
    evaluation_tracker = EvaluationTracker(
        output_dir="./results",
        save_details=False,
        push_to_hub=False,
    )
    pipeline_params = PipelineParameters(
        launcher_type=ParallelismManager.ACCELERATE,
        custom_tasks_directory=CUSTOM_TASKS_DIRECTORY,
        # Remove the 2 parameters below once your configuration is tested
        max_samples=max_samples,
    )

    tasks = build_tasks_name()
    return Pipeline(
        tasks=tasks,
        pipeline_parameters=pipeline_params,
        evaluation_tracker=evaluation_tracker,
        model_config=create_model_config(model_name, config),
    )


def test_model(model_name, max_samples=None, config : PipelineConfig = PipelineConfig()):
    pipeline = build_pipeline(model_name, max_samples, config)
    pipeline.evaluate()
    pipeline.save_and_push_results()
    pipeline.show_results()

