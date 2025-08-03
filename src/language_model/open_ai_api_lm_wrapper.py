# pylint: disable=inconsistent-return-statements
import time
from abc import ABC, abstractmethod
from typing import List, Dict

from src.language_model.init_function_calling import init_function_calling


class OpenAIAPILMWrapper(ABC):
    def __init__(
        self,
        model_name: str,
        extra_params: Dict,
        use_function_calling: bool = True,
        max_retries: int = 10,
    ):
        self.model_name = model_name
        self._extra_params = extra_params
        self.max_retries = max_retries
        self.use_function_calling = use_function_calling
        self.tool_choices = "required"

    @abstractmethod
    def _inner_generate_fn(self, prompt: List) -> Dict:
        pass

    def init_function_calling(self, labels: List[str], tool_choices: str) -> None:
        if self.use_function_calling:
            open_ai_call = (
                "claude" not in self.model_name.lower()
            )  # False for Anthropic model, True for the rest
            self._extra_params.update(
                init_function_calling(
                    labels=labels, tool_choices=tool_choices, open_ai_call=open_ai_call
                )
            )

    def predict(self, text: str) -> Dict:
        prompt = self.format_prompt(text)
        generated_completion = self.language_model_calling(prompt=prompt)

        final_prediction = self.extract_final_prediction(generated_completion)

        return {"prediction": final_prediction}

    @staticmethod
    def format_prompt(text: str) -> List:
        return [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": text},
                ],
            }
        ]

    def language_model_calling(self, prompt: List):
        return self._try_again(prompt=prompt)

    def _try_again(self, prompt: List, retries: int = 0):
        generated_completion = None
        if retries > self.max_retries:
            return generated_completion
        try:
            generated_completion = self._inner_generate_fn(prompt=prompt)
            return generated_completion
        except:
            time.sleep(5)
            self._try_again(prompt=prompt, retries=retries + 1)

    @staticmethod
    def extract_final_prediction(generated_completion) -> str:
        # Something the completion is incomplete, thus we validate that components are there.
        if generated_completion is None:
            final_prediction = None
        elif generated_completion.choices is None:
            final_prediction = None
        elif generated_completion.choices[0].message is None:
            final_prediction = None
        elif generated_completion.choices[0].message.tool_calls is None:
            # No tools call, but potentially a response in the raw message content.
            final_prediction = (
                generated_completion.choices[0]
                .message.content.strip()
                .replace(")", "")
                .strip()
            )
        else:
            prediction = (
                generated_completion.choices[0].message.tool_calls[0].function.arguments
            )
            try:
                final_prediction = eval(prediction).get("category")
            except:
                # Case where the prediction is not a proper dictionary.
                final_prediction = prediction
        return final_prediction
