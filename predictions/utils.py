import logging
import os

import huggingface_hub
from dotenv import load_dotenv


def hugging_face_login(token=None):
    """
    Login the user to the HuggingFace Hub with a token found in .env
    """
    try:
        if not token:
            load_dotenv()
            HF_TOKEN = os.getenv("HF_TOKEN", None)
            if HF_TOKEN is None:
                error_message = "HuggingFace Hub token not found in .env."
                logging.error(error_message)
                raise EnvironmentError(error_message)
        else:
            HF_TOKEN = token
        huggingface_hub.login(
            token=HF_TOKEN,
        )
    except Exception as e:
        error_message = f"Couldn't login to Huggingface hub : {e}"
        logging.error(error_message)
