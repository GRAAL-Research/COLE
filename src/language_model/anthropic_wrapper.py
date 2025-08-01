from typing import Dict

from anthropic import Anthropic
from pydantic import SecretStr

from src.language_model.open_ai_api_lm_wrapper import OpenAIAPILMWrapper


class AnthropicWrapper(OpenAIAPILMWrapper):
    def __init__(self, model_name: str, api_key: SecretStr, extra_params: Dict):
        super().__init__(model_name=model_name, extra_params=extra_params)
        self.client = Anthropic(api_key=api_key)

    def infer(self, text: str) -> Dict:
        prompt = self.format_prompt(text)
        generated_completion = self.language_model_calling(prompt=prompt)
        if generated_completion is None:
            final_prediction = None
        else:
            # We extract and parse the response (it is a literal string).
            final_prediction = generated_completion.content[0].input.get("category")
        return {"prediction": final_prediction}

    def _inner_generate_fn(self, text: str):
        return self.client.chat.completions.create(
            model=self.model_name,
            messages=text,
            n=1,
            **self._extra_params,
        )
