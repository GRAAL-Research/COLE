import os
from typing import Union

from pydantic import SecretStr

from predictions.all_llms import private_llm
from src.language_model.anthropic_wrapper import AnthropicWrapper
from src.language_model.deepseek_wrapper import DeepSeekWrapper
from src.language_model.google_wrapper import GoogleWrapper
from src.language_model.mistral_wrapper import MistralWrapper
from src.language_model.open_ai_wrapper import OpenAIWrapper
from src.language_model.xai_wrapper import XAIWrapper


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

    api_key = os.getenv(key_name, None)

    if api_key is None:
        raise ValueError(f"API key {key_name} not found.")
    return SecretStr(api_key)


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
        elif model_name in private_llm["mistral"]:
            extra_params = {}
            model = MistralWrapper(
                model_name=model_name, api_key=api_key, extra_params=extra_params
            )
        else:
            raise NotImplementedError("Not implemented yet.")
    else:
        raise ValueError(f"Model name {model_name} not found.")

    return model
