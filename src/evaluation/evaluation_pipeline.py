from predictions import utils
import logging
from predictions.all_llms import llms
from src.model.hugging_face_model import HFLLMModel
from src.evaluation.model_evaluator import ModelEvaluator
from src.task.task_factory import tasks_factory
import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
    "--test",
    help="if set to true, the system will default to testing only a small model with a few examples",
    default=False,
    type=bool,
)
parser.add_argument(
    "--max_examples",
    "-m",
    help="the maximum number of examples to use, defaults to None",
    type=int,
    default=None,
)
parser.add_argument(
    "--token",
    "-t",
    help="input your HuggingFace token to fetch models",
    type=str,
    default=None,
)
parser.add_argument(
    "--models_name",
    "-mn",
    help="the name of the model(s) to load",
    type=str,
    default=None,
)

parser.add_argument(
    "--batch_size",
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
    if args.models_name in llms.keys():
        models = llms[args.models_name]
    else:
        models = args.models_name.split(",")

logging.warning("starting Evaluation")
for model_name in models:
    try:
        model = HFLLMModel(model_name, batch_size=args.batch_size)
        logging.warning("creating model")
        evaluator = ModelEvaluator()
        logging.warning("evaluating model")
        evaluator.evaluate_subset(model, tasks, args.max_examples)
        logging.warning("saving results")
        evaluator.save_results("./results")
        evaluator.compute_metrics()
        evaluator.save_metrics("./results")
    except Exception as e:
        logging.error(f"Evaluation failed for model {model_name}: {e}")
        continue
