from typing import Dict
import logging


def get_customs_keys(dictionary: dict) -> Dict:
    for k, v in dictionary.items():
        if "custom" not in k:
            error_msg = "The dictionary is not formated as expected, a task should be written as 'custom|TASK|0|0'."

            raise ValueError("")

    return {k.split("|")[1]: v for k, v in dictionary.items()}
