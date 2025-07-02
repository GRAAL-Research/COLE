import argparse
import traceback

import utils
from offline_evaluation.all_llms import llms
from src.light_eval_custom.pipeline import test_model, PipelineConfig

TEST_MAX_EXAMPLES = 5
TEST_MODEL = "distilbert/distilgpt2"
LLMS = llms

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
    "--backend",
    "-b",
    help="the backend to use - vllm or transformers",
    type=str,
    default="vllm",
)
parser.add_argument(
    "--batch_size",
    type=int,
    default=8,

)
parser.add_argument("--max_seq_length",type=int,default=2048)
args = parser.parse_args()

if __name__ == "__main__":
    config = PipelineConfig(backend=args.backend,batch_size=args.batch_size,max_length=args.max_seq_length)
    print("used backend:", args.backend)
    utils.hugging_face_login(args.token)
    print("---------Logged in HuggingFace !")
    if args.test:
        print(
            f"Initiating Tests on {TEST_MODEL}, with max_samples set to {TEST_MAX_EXAMPLES}"
        )
        test_model(TEST_MODEL, max_samples=TEST_MAX_EXAMPLES)

    else:

        if args.models_name is not None:
            if args.models_name in llms.keys():
                models = llms[args.models_name]
            else:
                models = args.models_name.split(",")
        else:
            models = LLMS["all"]

        print(args.max_examples)
        skipped_models = []
        for model in models:
            try:
                test_model(model, max_samples=args.max_examples, config=config)
            except Exception as e:
                print("Exception occured", traceback.format_exc(), f"model: {model} was skipped")
                skipped_models.append(model)

            print(f"end of model test {model}")
        print(f"skipped models: {skipped_models}")
