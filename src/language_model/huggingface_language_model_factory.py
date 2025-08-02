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
        if "chocolatine" in model_name.lower():
            extra_args = {"padding_side": "left"}
        else:
            extra_args = {}
        tokenizer = AutoTokenizer.from_pretrained(
            model_name, token=huggingface_token, **extra_args
        )
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
    elif model_name in private_llm["mistral"]:
        key_name = "mistral_token"
    elif model_name in private_llm["xai"]:
        key_name = "XAI_API_KEY"
    elif model_name in private_llm["google"]:
        key_name = "gcp_key"
    else:
        raise ValueError(f"Model name {model_name} not found.")

    api_key = SecretStr(os.getenv(key_name))

    if api_key is None:
        raise ValueError(f"API key {key_name} not found.")
    return api_key
