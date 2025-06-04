from safetensors.torch import load_model

from Model import Model
from transformers import AutoModel, pipeline, AutoTokenizer, AutoModelForCausalLM

from Utils import omit_none

MODEL_CACHE = "./Loaded_Models"

class HFModel(Model):

    def __init__(self, model_name, task="text-generation", token=None, lazy_load=True):
        super().__init__(model_name)
        self.model, self.tokenizer, self.pipe, self.loaded = None, None, None, False
        self.task = task
        self.token = token
        if not lazy_load:
            self.load_model(model_name, task=task, token=token)

    def create_model(self, model_name, token=None):
        args = self.get_model_args(token)
        new_model = AutoModel.from_pretrained(model_name, **args)
        return new_model

    def get_model_args(self, token):
        return omit_none(
            use_auth_token=token,
            cache_dir=MODEL_CACHE
        )

    def create_tokenizer(self, model_name, token=None):
        args = omit_none(use_auth_token=token, )
        tokenizer = AutoTokenizer.from_pretrained(model_name, **args)
        return tokenizer

    def infer(self, prompt: str, conditions=None) -> str:
        if not self.loaded:
            self.load_model(self.model_name, task=self.task, token=self.token)
        return self.pipe(prompt)

    def change_task(self, task):
        try:
            self.pipe.task = task
        except Exception:
            print(f"Failed to change task to {task}")

    def load_model(self, model_name, task, token):
        self.model = self.create_model(model_name, token)
        self.tokenizer = self.create_tokenizer(model_name, token)
        self.pipe = pipeline(task=task, model=self.model, tokenizer=self.tokenizer,return_full_text=False)
        self.loaded = True

    def unload_model(self):
        self.tokenizer,self.model,self.pipe = None, None, None
        self.loaded = False


class HFLLMModel(HFModel):
    def __init__(self, model_name, token=None):
        super().__init__(model_name, "text-generation", token)

    def create_model(self, model_name, token=None):
        args = self.get_model_args(token)
        model = AutoModelForCausalLM.from_pretrained(model_name, **args)
        return model

    def infer(self, prompt: str, conditions=None) -> str:
        if not self.loaded:
            self.load_model(self.model_name, task=self.task, token=self.token)
        return self.pipe(prompt)[0]["generated_text"]

