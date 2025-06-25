import os

import huggingface_hub
from dotenv import load_dotenv


def omit_none(**kwargs):
    return {k:v for k,v in kwargs.items() if v is not None}

def create_directory( directory):
    try:
        os.makedirs(directory, exist_ok=True)
    except Exception as e:
        print(f" Couldn't create directory {directory} : {e}")
def hugging_face_login():
    try :
        load_dotenv()
        HF_TOKEN = os.getenv('HF_TOKEN')
        huggingface_hub.login(token=HF_TOKEN)
    except Exception as e:
        print(f"Couldn't login to Huggingface hub : {e})

