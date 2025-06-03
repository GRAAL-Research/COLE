import os
from abc import abstractmethod

from anthropic import Anthropic

from dotenv import load_dotenv
load_dotenv(".env")
api_key = os.getenv("ANTHROPIC_API_KEY")
if api_key is None:
    raise RuntimeError("ANTHROPIC_API_KEY non défini dans .env")

claude_client = Anthropic(api_key=api_key)

def make_claude_inference(model_name: str):

    def infer(prompt: str, conditions=None) -> str:
        response = claude_client.messages.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512,
            temperature=0.0,
        )
        # Extraire uniquement le texte de la réponse
        return response.content[0].text.strip() if response.content else ""
    return infer

class Model:
    def __init__(self, model_name: str, inference_callback=None, prompt_only=True):
        self.model_name = model_name

        if inference_callback is not None:
            self.infer = inference_callback

        self.prompt_only = prompt_only

    @abstractmethod
    def infer(self, prompt: str, conditions=None) -> str:
        return "0"