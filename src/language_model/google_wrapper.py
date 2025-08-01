from typing import Dict

from openai import OpenAI
from pydantic import SecretStr

from src.language_model.open_ai_api_lm_wrapper import OpenAIAPILMWrapper


class GoogleWrapper(OpenAIAPILMWrapper):
    def __init__(self, model_name: str, api_key: SecretStr, extra_params: Dict):
        super().__init__(model_name=model_name, extra_params=extra_params)
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )

    def infer(self, text: str) -> Dict:
        prompt = self.format_prompt(text)
        generated_completion = self.language_model_calling(prompt=prompt)
        if generated_completion is None:
            final_prediction = None
        else:
            # We extract and parse the response (it is a literal string).
            prediction = (
                generated_completion.choices[0].message.tool_calls[0].function.arguments
            )
            try:
                final_prediction = eval(prediction).get("category")
            except:
                # Case where the prediction is not a proper dictionary.
                final_prediction = prediction
        return {"prediction": final_prediction}

    def _inner_generate_fn(self, prompt: Dict):
        return self.client.chat.completions.create(
            model=self.model_name,
            messages=prompt,
            **self._extra_params,
        )
