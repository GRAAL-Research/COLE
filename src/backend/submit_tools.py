from typing import Dict
import logging


def convert_custom_dict_to_task_dict(dictionary: dict) -> Dict:
    for k, v in dictionary.items():
        if "custom" not in k:
            error_msg = "The dictionary is not formated as expected, a task should be written as 'custom|TASK|0|0'."
            logging.error(error_msg)
            raise ValueError(error_msg)
        elif len(k.split("|")) < 4:
            error_msg = "The dictionary is not formated as expected, a task should be written as 'custom|TASK|0|0'."
            logging.error(error_msg)
            raise ValueError(error_msg)

    return {k.split("|")[1]: v for k, v in dictionary.items()}
