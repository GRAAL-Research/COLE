from predictions.all_llms import small_llm, llms, private_llm
from src.language_model.baseline import RandomBaselineModel
from src.language_model.hugging_face_lm import HFLLMModel
from src.language_model.language_model_abstraction import LanguageModel
from src.language_model.private_lm import RemoteLLMModel


def model_factory(model_name: str, batch_size: int) -> LanguageModel:
    if model_name == "RandomBaselineModel":
        model = RandomBaselineModel(model_name="random_baseline")
    elif model_name in private_llm:
        model = RemoteLLMModel(model_name=model_name)
    elif model_name in llms or model_name in small_llm:
        model = HFLLMModel(model_name=model_name, batch_size=batch_size)
    else:
        raise ValueError(f"Model {model_name} not supported.")
    return model
