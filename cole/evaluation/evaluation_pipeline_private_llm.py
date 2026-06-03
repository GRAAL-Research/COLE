import argparse
import gc
import logging
from datetime import datetime

import wandb
from dotenv import load_dotenv
from tqdm import tqdm

from predictions.all_llms import private_llm
from cole.evaluation.llm_evaluator import ModelEvaluator
from cole.evaluation.tools import str2bool
from cole.language_model.private_lm import RemoteLLMModel
from cole.task.task_factory import tasks_factory
from cole.task.task_names import COLETasks, BorealTasks

load_dotenv(".env")

parser = argparse.ArgumentParser()
parser.add_argument(
    "--test",
    help="If set to true, the system will default to testing only a small model with a few examples.",
    default=False,
    type=str2bool,
)
parser.add_argument(
    "--max_examples",
    "-m",
    help="The maximum number of examples to use, defaults to None.",
    type=int,
    default=None,
)
parser.add_argument(
    "--models_name",
    "-mn",
    help="The name of the model(s) to load.",
    type=str,
    default=None,
)
parser.add_argument(
    "--provider_name",
    "-pn",
    help="The name of the LLM provider to load.",
    type=str,
    default=None,
    choices=list(private_llm.keys()),
)
parser.add_argument(
    "--tasks_group",
    help="The task group to test",
    type=str,
    default=None,
    choices=["all", "cole", "boreal", "comparison"],
)

args = parser.parse_args()

if args.tasks_group == "all":
    tasks_names = list(COLETasks) + list(BorealTasks)
    from cole import complete as project
elif args.tasks_group == "cole":
    tasks_names = list(COLETasks)
    from cole import cole as project
elif args.tasks_group == "boreal":
    tasks_names = list(BorealTasks)
    from cole import boreal as project
elif args.tasks_group == "comparison":
    tasks_names = ["frcoe"]
    from cole import comparison as project
else:
    raise ValueError("Invalid value for tasks_group")

tasks = tasks_factory(tasks_names)

models = []
if args.models_name is not None:
    if args.models_name in private_llm:
        models = private_llm[args.models_name]
    else:
        models = args.models_name.split(",")
elif args.provider_name is not None:
    models = private_llm[args.provider_name]
else:
    models = private_llm["all"]

logging.info("Starting Evaluation")

time_start = datetime.now()

for model_name in tqdm(
    models, total=len(models), desc="Processing LLM inference on tasks."
):
    model = None
    evaluator = None
    try:
        model = RemoteLLMModel(model_name=model_name)
        logging.info("Creating model")
        evaluator = ModelEvaluator()
        logging.info("Evaluating model")

        exp_name = f"{model_name}"
        wandb.init(
            project=project,
            entity="doctorate",
            config={"model_name": model_name, "tasks": "; ".join(tasks_names)},
            name=exp_name,
        )

        predictions_payload = evaluator.evaluate_subset(model, tasks, args.max_examples)
        logging.info("Writing predictions to WandB.")
        wandb.log(predictions_payload)

        logging.info("Saving results")
        evaluator.save_results("./results")

        metrics_payload = evaluator.compute_metrics()
        evaluator.save_metrics("./results")
        wandb.log(metrics_payload)

    except Exception as e:
        error_message = f"Evaluation failed for model {model_name}: {e}"
        logging.error(error_message)
        wandb.finish(exit_code=1)
        continue
    finally:
        # Memory cleaning
        del model
        del evaluator
        gc.collect()
        wandb.finish(exit_code=0)

time_end = datetime.now()
info_message = f"End time: {time_end}"
logging.info(info_message)
elapsed_time = time_end - time_start
info_message = f"Elapsed time: {elapsed_time}"
logging.info(info_message)
