import torch
from transformers import (
    AutoTokenizer,
    BitsAndBytesConfig,
    AutoModelForCausalLM,
    AutoModelForMaskedLM,
)
from unsloth import FastLanguageModel


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
