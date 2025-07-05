import os

import huggingface_hub
from dotenv import load_dotenv


def hugging_face_login(token=None):
    try:
        if not token:
            load_dotenv()
            HF_TOKEN = os.getenv("HF_TOKEN")
        else:
            HF_TOKEN = token
        huggingface_hub.login(token=HF_TOKEN)
    except Exception as e:
        print(f"Couldn't login to Huggingface hub : {e}")
