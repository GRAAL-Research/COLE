from pipeline import test_model
import argparse
import Utils

TEST_MAX_EXAMPLES = 5
TEST_MODEL = "distilbert/distilgpt2"

parser = argparse.ArgumentParser()
parser.add_argument("--test",
                    help="if set to true, the system will default to testing only a small model with a few examples",
                    default=False,
                    type=bool)
parser.add_argument("--max_examples", "-m",
                    help="the maximum number of examples to use, defaults to None",
                    type=int,
                    default=None)
parser.add_argument("--token", "-t",
                    help="input your HuggingFace token to fetch models",
                    type=str,
                    default=None)
parser.add_argument("--models_name", "-mn",
                    help="the name of the model(s) to load",
                    type=str,
                    default=None)

args = parser.parse_args()

if __name__ == "__main__":
    Utils.hugging_face_login(args.token)
    print("Logged in HuggingFace !")
    if args.test:
        print(f"Initiating Tests on {TEST_MODEL}, with max_samples set to {TEST_MAX_EXAMPLES}")
        test_model(TEST_MODEL, max_samples=TEST_MAX_EXAMPLES)

    else:

        if args.models_name is not None:
            models = args.models_name.split(",")
        else :
            models = ["unsloth/Llama-3.2-3B-unsloth-bnb-4bit",

        "unsloth/Llama-3.2-3B-Instruct-unsloth-bnb-4bit",

        "unsloth/mistral-7b-v0.3-bnb-4bit"]

        print(args.max_examples)

        for model in models:
            test_model(model, max_samples=args.max_examples)
            print(f"end of model test {model}")
