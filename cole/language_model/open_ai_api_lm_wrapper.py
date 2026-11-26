# pylint: disable=inconsistent-return-statements
import logging
import time
from abc import ABC, abstractmethod
from typing import List, Dict

from cole import NA_VALUE
from cole.language_model.init_function_calling import init_function_calling


class OpenAIAPILMWrapper(ABC):
    def __init__(
        self,
        model_name: str,
        extra_params: Dict,
        use_function_calling: bool = True,
        max_retries: int = 10,
    ):
        self.model_name = model_name
        # Never mutate the caller's dict, and keep an untouched copy so that per-task
        # parameters (tools, tool_choice) can be dropped between tasks.
        self._base_extra_params: Dict = dict(extra_params)
        self._extra_params: Dict = dict(extra_params)
        self.retry_delay_seconds = 5.0
        self.max_retries = max_retries
        self.use_function_calling = use_function_calling
        self.tool_choices = "required"

        self._none_prediction_counter = 0
        self._max_retries_counter = 0

    @abstractmethod
    def _inner_generate_fn(self, prompt: List) -> Dict:
        pass

    def init_function_calling(self, labels: List[str], tool_choices: str) -> None:
        if self.use_function_calling:
            open_ai_api_call = (
                "claude" not in self.model_name.lower()
            )  # False for Anthropic model, True for the rest
            # Build a new dict instead of updating in place.
            self._extra_params = {
                **self._base_extra_params,
                **init_function_calling(
                    labels=labels,
                    tool_choices=tool_choices,
                    open_ai_api_call=open_ai_api_call,
                ),
            }

    def reset_function_calling(self) -> None:
        """Drop the label-constrained tools so a generative task is not forced into a label enum."""
        self._extra_params = dict(self._base_extra_params)

    def predict(self, text: str, extract_label: bool = True) -> Dict:
        """
        Predict for one text.

        Args:
            text: The prompt.
            extract_label: True for classification tasks (label post-processing is applied),
                False for generative/extractive tasks (the raw answer is kept as is).
        """
        prompt = self.format_prompt(text)
        generated_completion = self.language_model_calling(prompt=prompt)

        final_prediction = self.extract_final_prediction(
            generated_completion, extract_label=extract_label
        )

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

    def _try_again(self, prompt: List):
        """Call the API with a bounded number of retries. Return None when all attempts failed."""
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                return self._inner_generate_fn(prompt=prompt)
            except Exception as error:  # pylint: disable=broad-exception-caught
                last_error = error
                logging.warning(
                    "API call failed (attempt %s/%s): %r",
                    attempt + 1,
                    self.max_retries + 1,
                    error,
                )
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay_seconds)
        logging.warning(
            "Max retries exceeded: %s. Last error: %r", self.max_retries, last_error
        )
        self._max_retries_counter += 1
        return None

    def extract_final_prediction(
        self, generated_completion, extract_label: bool = True
    ) -> str:
        if "claude" in self.model_name.lower():
            final_prediction = self._extract_anthropic(
                generated_completion, extract_label
            )
        else:
            final_prediction = self._extract_openai(generated_completion, extract_label)

        if final_prediction is None:
            # Case were final prediction is None. Labels must stay castable as int (-1);
            # generative answers use an explicit "NA" marker that the generative metrics
            # exclude and report. In both cases it can not yield better results.
            self._none_prediction_counter += 1
            return f"{NA_VALUE}" if extract_label else "NA"
        if not extract_label:
            # Generative/extractive task: keep the answer untouched.
            return final_prediction
        return self._clean_label(final_prediction)

    @staticmethod
    def _extract_anthropic(generated_completion, extract_label: bool):
        if generated_completion is None or generated_completion.content is None:
            return None
        if not extract_label:
            # Generative task: Anthropic answers with plain text blocks (no tool input).
            text_blocks = [
                block.text
                for block in generated_completion.content
                if getattr(block, "text", None)
            ]
            return "".join(text_blocks).strip() or None
        tool_blocks = [
            block
            for block in generated_completion.content
            if getattr(block, "type", None) == "tool_use"
        ]
        if not tool_blocks:
            # tool_choice "auto": the model may answer in plain text instead.
            text = "".join(
                getattr(block, "text", "") or ""
                for block in generated_completion.content
            ).strip()
            return text or None
        tool_input = tool_blocks[0].input
        if tool_input is None:
            return None
        try:
            return tool_input.get("category")
        except:  # pylint: disable=bare-except
            # Case where the prediction is not a proper dictionary.
            return tool_input

    @staticmethod
    def _extract_openai(generated_completion, extract_label: bool):
        # Sometimes the completion is incomplete, thus we validate that components are there.
        if generated_completion is None or generated_completion.choices is None:
            return None
        message = generated_completion.choices[0].message
        if message is None:
            return None
        if message.tool_calls is None:
            if message.content is None:
                return None
            # No tools call, but potentially a response in the raw message content.
            content = message.content.strip()
            return content.replace(")", "").strip() if extract_label else content
        prediction = message.tool_calls[0].function.arguments
        try:
            return eval(prediction).get("category")  # pylint: disable=eval-used
        except:  # pylint: disable=bare-except
            # Case where the prediction is not a proper dictionary.
            return prediction

    @staticmethod
    def _clean_label(prediction: str) -> str:
        """Post-process a classification answer so it becomes a bare label (single digit)."""
        if "La réponse est" in prediction or ":" in prediction:
            # To handle case where the LLM return the premise to the last query.
            return prediction.split(":")[-1].strip().replace(" ", "")
        # Cases where the response is accompanied by other string elements, but it should be a
        # single digit. (Legacy order kept: "10" and "11" are caught by "1"/"0" first.)
        for digit in "0123456789":
            if digit in prediction:
                return digit
        return prediction

    def print_none(self) -> None:
        if self._none_prediction_counter > 0:
            logging_message = f"Number of None: {self._none_prediction_counter}."
            logging.warning(logging_message)
        if self._max_retries_counter > 0:
            logging_message = f"Number of max retries exceeded occurrence: {self._max_retries_counter}."
            logging.warning(logging_message)
