import logging
import os

import huggingface_hub
from dotenv import load_dotenv


def hugging_face_login(token=None):
    """login the user to the HuggingFace Hub with a token found in .env"""
    try:
        print(token)
        if not token:
            load_dotenv()
            HF_TOKEN = os.getenv("HF_TOKEN")
        else:
            HF_TOKEN = token
        print("token", token)
        huggingface_hub.login(
            token=HF_TOKEN,
        )
    except Exception as e:
        logging.error(f"Couldn't login to Huggingface hub : {e}")
