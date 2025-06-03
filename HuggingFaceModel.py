from colle.Model import Model
from transformers import AutoModel, pipeline, AutoTokenizer

MODEL_CACHE = "./Loaded_Models"


class HFModel(Model):

    def __init__(self, model_name, token=None):
        super().__init__(model_name)
        if token is not None:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name,use_auth_token=token,cache_dir=MODEL_CACHE)
            self.model = AutoModel.from_pretrained(model_name,use_auth_token=token,cache_dir=MODEL_CACHE)
        else:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name,cache_dir=MODEL_CACHE)
            self.model = AutoModel.from_pretrained(model_name,cache_dir=MODEL_CACHE,device_map={"": "cpu"},low_cpu_mem_usage=True)

        self.pipe = pipeline(task="text-generation", model=self.model, tokenizer=self.tokenizer)

    def infer(self, prompt: str, conditions=None) -> str:
        return self.pipe(prompt)

model = HFModel("jpacifico/French-Alpaca-Llama3-8B-Instruct-v1.0")
model.infer("What's my name ?")