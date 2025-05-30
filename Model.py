class Model:
    def __init__(self,model_name, inference_callback = None,prompt_only = True):
        self.model_name = model_name
        if inference_callback is not None:
            self.infer = inference_callback
        self.prompt_only = prompt_only

    #Override to return an inference result by model
    def infer(self, prompt, conditions = None):
        return "0"