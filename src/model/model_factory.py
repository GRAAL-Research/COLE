import torch
from transformers import (
    AutoTokenizer,
    BitsAndBytesConfig,
    AutoModelForCausalLM,
    AutoModelForMaskedLM,
)
from unsloth import FastLanguageModel


def model_tokenizer_factory(
    model_name,
    max_seq_length: int,
    huggingface_token: str,
    gpu_memory_utilization: float,
):
    load_in_4bit = True

    if "chocolatine" in model_name.lower():

        # bitsandbytes config
        USE_NESTED_QUANT = True  # use_nested_quant
        BNB_4BIT_COMPUTE_DTYPE = "bfloat16"  # bnb_4bit_compute_dtype

        compute_dtype = getattr(torch, BNB_4BIT_COMPUTE_DTYPE)
        bnb_configs = BitsAndBytesConfig(
            load_in_4bit=load_in_4bit,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=compute_dtype,
            bnb_4bit_use_double_quant=USE_NESTED_QUANT,
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

        if "saul" in model_name.lower():
            tokenizer.pad_token = tokenizer.eos_token

    elif "bert" in model_name.lower():
        # For Debug.
        model = AutoModelForMaskedLM.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
    else:
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name,
            max_seq_length=max_seq_length,
            device_map="sequential",
            dtype=None,
            load_in_4bit=load_in_4bit,
            token=huggingface_token,
            gpu_memory_utilization=gpu_memory_utilization,
            fast_inference=True,
        )

    model.eval()
    return model, tokenizer
