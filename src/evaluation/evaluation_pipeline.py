import argparse
import logging
import gc
from datetime import datetime
import torch
from predictions import utils
from predictions.all_llms import llms
from src.model.hugging_face_model import HFLLMModel
from src.evaluation.model_evaluator import ModelEvaluator
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
    default=8,
)

parser.add_argument("--max_seq_length", type=int, default=4096)
args = parser.parse_args()

utils.hugging_face_login(args.token)

tasks = tasks_factory(
    [
        "piaf",
        "qfrblimp",
        "allocine",
        "qfrcola",
        "gqnli",
        "opus_parcus",
        "paws_x",
        "fquad",
        "sickfr",
        "sts22",
        "xnli",
    ]
)

models = []
if args.models_name is not None:
    if args.models_name in llms:
        models = llms[args.models_name]
    else:
        models = args.models_name.split(",")

logging.warning("starting Evaluation")

time_start = datetime.now()

for model_name in models:
    try:
        model = HFLLMModel(model_name, batch_size=args.batch_size)
        logging.info("creating model")
        evaluator = ModelEvaluator()
        logging.info("evaluating model")
        evaluator.evaluate_subset(model, tasks, args.max_examples)
        logging.info("saving results")
        evaluator.save_results("./results")
        evaluator.compute_metrics()
        evaluator.save_metrics("./results")
    except Exception as e:
        error_message = f"Evaluation failed for model {model_name}: {e}"
        logging.error(error_message)
        continue
    finally:
        if "model" in locals():
            del model
        if "evaluator" in locals():
            del evaluator
        gc.collect()
        torch.cuda.empty_cache()

time_end = datetime.now()
info_message = f"End time: {time_end}"
logging.info(info_message)
elapsed_time = time_end - time_start
info_message = f"Elapsed time: {elapsed_time}"
logging.info(info_message)
