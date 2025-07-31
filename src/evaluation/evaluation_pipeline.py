import argparse
import gc
import logging
from datetime import datetime

import torch
import wandb
from tqdm import tqdm

from predictions.all_llms import llms
from src.evaluation.model_evaluator import ModelEvaluator
from src.evaluation.model_factory import model_factory
from src.evaluation.tools import split_llm_list
from src.task.task_factory import tasks_factory

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
    default=64,
)

parser.add_argument(
    "--llm_split",
    help="The split of the LLMs list to use. It can be '1', '2' or '3'.",
    type=int,
    default=None,
)

args = parser.parse_args()

tasks_names = [
    "allocine",
    "daccord",
    "qfrcore",
    "fquad",
    "fracas",
    "french_boolq",
    "gqnli",
    "mms",
    "mnli-nineeleven-fr-mt",
    "multiblimp",
    "paws_x",
    "piaf",
    "qfrblimp",
    "qfrcola",
    "rte3-french",
    "sickfr",
    "sts22",
    "termes_quebecoises",
    "wino_x_lm",
    "wino_x_mt",
    "xnli",
]

tasks = tasks_factory(tasks_names)

models = []
if args.models_name is not None:
    if args.models_name in llms:
        models = llms[args.models_name]
    elif args.models_name == "RandomBaselineModel":
        models = ["RandomBaselineModel"]
    else:
        models = args.models_name.split(",")
else:
    models = llms["all"]

models = split_llm_list(models=models, llm_split=args.llm_split)

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
            project="COLLE",
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
