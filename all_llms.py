import os

from dotenv import load_dotenv

from colle.HuggingFaceModel import HFModel

load_dotenv()

models_token_pairs = [
    {
    "models" : [
        "unsloth/Llama-3.2-3B-unsloth-bnb-4bit",

        "unsloth/Llama-3.2-3B-Instruct-unsloth-bnb-4bit",

        "unsloth/mistral-7b-v0.3-bnb-4bit",

        "unsloth/mistral-7b-instruct-v0.3-bnb-4bit",

        "unsloth/phi-4-unsloth-bnb-4bit",

        "unsloth/gemma-2-9b-bnb-4bit",

        "unsloth/gemma-2-9b-it-bnb-4bit",

        "unsloth/gemma-2-27b-bnb-4bit",

        "unsloth/gemma-2-27b-it-bnb-4bit",

        "unsloth/Qwen2.5-1.5B-unsloth-bnb-4bit",

        "unsloth/Qwen2.5-1.5B-Instruct-unsloth-bnb-4bit",

        "unsloth/Qwen2.5-3B-unsloth-bnb-4bit",

        "unsloth/Qwen2.5-3B-Instruct-unsloth-bnb-4bit",

        "unsloth/Qwen2.5-7B-unsloth-bnb-4bit",

        "unsloth/Qwen2.5-7B-Instruct-unsloth-bnb-4bit",

        "unsloth/Qwen2.5-14B-unsloth-bnb-4bit",

        "unsloth/Qwen2.5-14B-Instruct-unsloth-bnb-4bit"],

    "token" : os.getenv("")
    },
    {
    "models": [
        "jpacifico/Chocolatine-14B-Instruct-DPO-v1.2",

        "jpacifico/French-Alpaca-Llama3-8B-Instruct-v1.0"],

    "token": os.getenv("")
    },
    {
    "models": [
        "OpenLLM-France/Lucie-7B",

        "OpenLLM-France/Lucie-7B-Instruct-v1.1"],
    "token": os.getenv("")
    },
    {
    "models": [
        "unsloth/DeepSeek-R1-Distill-Qwen-7B-unsloth-bnb-4bit",

        "unsloth/DeepSeek-R1-Distill-Llama-8B-unsloth-bnb-4bit",

        "unsloth/DeepSeek-R1-Distill-Qwen-14B-unsloth-bnb-4bit",

        "unsloth/DeepSeek-R1-Distill-Qwen-32B-unsloth-bnb-4bit"],
    "token": os.getenv("deepseek_token")
    },
    {
    "models": [
        "prithivMLmods/Deepthink-Reasoning-7B",

        "prithivMLmods/Deepthink-Reasoning-14B"],
    "token": os.getenv('deepseek_token')
    },
    {
    "models": [
        "simplescaling/s1.1-32B",

        "unsloth/granite-3.2-8b-instruct-bnb-4bit",

        "CohereForAI/aya-23-8B",

        "unsloth/QwQ-32B-unsloth-bnb-4bit",

        "unsloth/OLMo-2-0325-32B-Instruct-bnb-4bit",

        "unsloth/OLMo-2-0325-32B-Instruct-unsloth-bnb-4bit",

        "allenai/OLMo-2-1124-13B-Instruct",

        "allenai/OLMo-2-1124-13B",

        "allenai/OLMo-2-1124-7B-Instruct",

        "allenai/OLMo-2-1124-7B",

        "unsloth/Mixtral-8x7B-Instruct-v0.1-unsloth-bnb-4bit",

        "unsloth/Mixtral-8x7B-v0.1-unsloth-bnb-4bit",

        "unsloth/reka-flash-3-unsloth-bnb-4bit",

        "unsloth/Llama-4-Scout-17B-16E-Instruct-unsloth-bnb-4bit",

        "unsloth/Llama-4-Scout-17B-16E-unsloth-bnb-4bit"],
    "token": os.getenv("")
    }]
def create_models():
    print("loading models")
    for pair in models_token_pairs:
        for model in pair["models"]:
            print(f"loading model {model}, token: {pair['token']}")
            model = HFModel(model, pair["token"])
            yield model
