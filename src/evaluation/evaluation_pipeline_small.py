import argparse
import gc
import logging
from datetime import datetime

import torch
import wandb
from tqdm import tqdm

from predictions.all_llms import small_llm
from src import WANDB_PROJECT
from src.evaluation.llm_evaluator import ModelEvaluator
from src.evaluation.llm_factory import model_factory
from src.task.task_factory import tasks_factory
from src.task.task_names import Tasks

parser = argparse.ArgumentParser()
parser.add_argument(
    "--test",
    help="If set to true, the system will default to testing only a small model with a few examples.",
    default=False,
    type=bool,
)
parser.add_argument(
    "--max_examples",
    "-m",
    help="The maximum number of examples to use, defaults to None.",
    type=int,
    default=None,
)
parser.add_argument(
    "--token",
    "-t",
    help="Input your HuggingFace token to fetch models.",
    type=str,
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
    "--batch_size",
    help="The batch size to use during the evaluation.",
    type=int,
    default=32,
)

parser.add_argument(
    "--skip_first_n",
    help="The number of LLM to skip in the list of split",
    type=int,
    default=None,
)

args = parser.parse_args()

tasks_names = list(Tasks)

tasks = tasks_factory(tasks_names)

models = []
if args.models_name is not None:
    if args.models_name in small_llm:
        models = small_llm[args.models_name]
    else:
        models = args.models_name.split(",")
else:
    models = small_llm["all"]

if args.skip_first_n is not None:
    models = models[args.skip_first_n :]

logging.info("Starting Evaluation")

time_start = datetime.now()

for model_name in tqdm(
    models, total=len(models), desc="Processing LLM inference on tasks."
):

    try:
        model = model_factory(model_name, batch_size=args.batch_size)
        logging.info("Creating model")
        evaluator = ModelEvaluator()
        logging.info("Evaluating model")

        exp_name = f"{model_name}"
        wandb.init(
            project=WANDB_PROJECT,
            entity="doctorate",
            config={"model_name": model_name, "tasks": "; ".join(tasks_names)},
            name=exp_name,
        )

        predictions_payload = evaluator.evaluate_subset(model, tasks, args.max_examples)
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
        if "model" in locals():
            del model
        if "evaluator" in locals():
            del evaluator
        gc.collect()
        torch.cuda.empty_cache()
        wandb.finish(exit_code=0)

time_end = datetime.now()
info_message = f"End time: {time_end}"
logging.info(info_message)
elapsed_time = time_end - time_start
info_message = f"Elapsed time: {elapsed_time}"
logging.info(info_message)
