import os
from typing import Union

import torch
from pydantic import SecretStr
from transformers import (
    AutoTokenizer,
    BitsAndBytesConfig,
    AutoModelForCausalLM,
    AutoModelForMaskedLM,
)
from unsloth import FastLanguageModel

from predictions.all_llms import private_llm
from src.language_model.anthropic_wrapper import AnthropicWrapper
from src.language_model.deepseek_wrapper import DeepSeekWrapper
from src.language_model.google_wrapper import GoogleWrapper
from src.language_model.open_ai_wrapper import OpenAIWrapper
from src.language_model.xai_wrapper import XAIWrapper


def hugging_face_language_model_tokenizer_factory(
    model_name,
    huggingface_token: str,
):
    if "chocolatine" in model_name.lower() or "lucie" in model_name.lower():

        compute_dtype = getattr(torch, "bfloat16")
        bnb_configs = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=compute_dtype,
            bnb_4bit_use_double_quant=True,
        )
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            token=huggingface_token,
            quantization_config=bnb_configs,
            load_in_8bit=False,  # Since we use 4bits
            trust_remote_code=True,
            attn_implementation="flash_attention_2",
            torch_dtype=torch.float16,
        )

        tokenizer = AutoTokenizer.from_pretrained(model_name, token=huggingface_token)
    elif "bloom" in model_name.lower():
        bnb_configs = BitsAndBytesConfig(load_in_8bit=True, low_cpu_mem_usage=True)

        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            token=huggingface_token,
            quantization_config=bnb_configs,
            trust_remote_code=True,
        )

        tokenizer = AutoTokenizer.from_pretrained(model_name, token=huggingface_token)
    elif "bert" in model_name.lower():
        # For Debug.
        model = AutoModelForMaskedLM.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
    else:
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name,
            max_seq_length=4096,
            device_map="sequential",
            dtype=None,
            load_in_4bit=True,
            token=huggingface_token,
        )

    model.eval()
    return model, tokenizer


def get_api_key(model_name: str) -> Union[SecretStr, None]:
    if model_name in private_llm["openai"]:
        key_name = "openai_api_key"
    elif model_name in private_llm["anthropic"]:
        key_name = "anthropic_token"
    elif model_name in private_llm["deepseek"]:
        key_name = "deepseek_token"
    elif model_name in private_llm["mistrail"]:
        key_name = "mistral_token"
    elif model_name in private_llm["xai"]:
        key_name = "XAI_API_KEY"
    elif model_name in private_llm["google"]:
        key_name = "gcp_key"
    else:
        return None
    api_key = SecretStr(os.getenv(key_name))

    if api_key is None:
        raise Exception(f"API key {key_name} not found.")
    else:
        return api_key


def private_language_model_factory(model_name):
    if model_name in private_llm["all"]:
        api_key = get_api_key(model_name)

        if model_name in private_llm["openai"]:
            if "o1" in model_name and not "o1-mini" in model_name:
                extra_params = {
                    "reasoning_effort": "low"
                }  # Otherwise take too many tokens and stop the process.

            else:
                extra_params = {}
            model = OpenAIWrapper(
                model_name=model_name, api_key=api_key, extra_params=extra_params
            )
        elif model_name in private_llm["anthropic"]:
            extra_params = {"max_tokens": 5012}
            model = AnthropicWrapper(
                model_name=model_name, api_key=api_key, extra_params=extra_params
            )
        elif model_name in private_llm["deepseek"]:
            extra_params = {"timeout": 120}
            # DeepSeek reasoner does not support function calling
            use_function_calling = model_name == "deepseek-reasoner"
            model = DeepSeekWrapper(
                model_name=model_name,
                api_key=api_key,
                extra_params=extra_params,
                use_function_calling=use_function_calling,
            )
        elif model_name in private_llm["xai"]:
            extra_params = {}
            model = XAIWrapper(
                model_name=model_name, api_key=api_key, extra_params=extra_params
            )
        elif model_name in private_llm["google"]:
            extra_params = {}
            model = GoogleWrapper(
                model_name=model_name, api_key=api_key, extra_params=extra_params
            )
        else:
            raise NotImplementedError("Not implemented yet.")
    return model
