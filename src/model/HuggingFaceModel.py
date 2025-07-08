from transformers import AutoModel, pipeline, AutoTokenizer, AutoModelForCausalLM


from Model import Model

MODEL_CACHE = "./Loaded_Models"


def chunk_list(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i : i + chunk_size]


def omit_none(**kwargs):
    return {k: v for k, v in kwargs.items() if v is not None}


class HFModel(Model):

    def __init__(
        self,
        model_name,
        task="text-generation",
        token=None,
        lazy_load=True,
        batch_size=8,
    ):
        super().__init__(model_name)
        self.model_name = model_name
        self.model, self.tokenizer, self.pipe, self.loaded = None, None, None, False
        self.task = task
        self.token = token
        self.batch_size = batch_size
        if not lazy_load:
            self.load_model(model_name, task=task, token=token)

    def create_model(self, model_name, token=None):
        args = self.get_model_args(token)
        new_model = AutoModel.from_pretrained(model_name, **args)
        return new_model

    def get_model_args(self, token):
        return omit_none(use_auth_token=token, cache_dir=MODEL_CACHE)

    def create_tokenizer(self, model_name, token=None):
        args = omit_none(
            use_auth_token=token,
        )
        tokenizer = AutoTokenizer.from_pretrained(model_name, **args)
        return tokenizer

    def infer(self, prompts: str, conditions=None):
        if not self.loaded:
            self.load_model(self.model_name, task=self.task, token=self.token)
        if isinstance(prompts, str):
            prompts = [prompts]

        all_outputs = []
        for sub_batch in chunk_list(prompts, self.batch_size):
            try:
                outputs = self.pipe(sub_batch)
            except Exception as e:
                print(f" Échec inference batch {sub_batch[:2]} : {e}")
                outputs = [{} for _ in sub_batch]
            all_outputs.extend(outputs)

        return all_outputs

    def change_task(self, task):
        try:
            self.pipe.task = task
        except Exception:
            print(f"Failed to change task to {task}")

    def load_model(self, model_name, task, token):
        try:
            self.model = self.create_model(model_name, token)
            self.tokenizer = self.create_tokenizer(model_name, token)
            self.pipe = pipeline(
                task=task,
                model=self.model,
                tokenizer=self.tokenizer,
                return_full_text=False,
            )
            self.loaded = True
        except Exception as e:
            print(f"️ Impossible de charger le modèle {model_name} : {e}")
            self.loaded = False

    def unload_model(self):
        self.tokenizer, self.model, self.pipe = None, None, None
        self.loaded = False


class HFLLMModel(HFModel):
    def __init__(self, model_name, token=None, batch_size=8):
        super().__init__(model_name, "text-generation", token, batch_size=batch_size)

    def create_model(self, model_name, token=None):
        args = self.get_model_args(token)
        model = AutoModelForCausalLM.from_pretrained(model_name, **args)
        return model

    def infer(self, prompts: str | list[str], max_new_tokens=3, conditions=None):
        if not self.loaded:
            self.load_model(self.model_name, task=self.task, token=self.token)
        if isinstance(prompts, str):
            prompts = [prompts]
        all_texts = []
        for sub_batch in chunk_list(prompts, self.batch_size):
            try:
                batch_outputs = self.pipe(sub_batch, max_new_tokens=max_new_tokens)
            except Exception as e:
                print(f"️ Failed inference batch {sub_batch[:2]} : {e}")
                batch_outputs = [{} for _ in sub_batch]
            for single_output in batch_outputs:
                if isinstance(single_output, list) and len(single_output) > 0:
                    all_texts.append(single_output[0].get("generated_text", ""))
                else:
                    text = (
                        single_output.get("generated_text", "")
                        if isinstance(single_output, dict)
                        else ""
                    )
                    all_texts.append(text)

        return all_texts
