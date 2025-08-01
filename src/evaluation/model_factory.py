from src.model.baseline_model import RandomBaselineModel
from src.model.hugging_face_model import HFLLMModel


def model_factory(model_name: str, batch_size: int):
    match model_name:
        case "RandomBaselineModel":
            return RandomBaselineModel(model_name="random_baseline")
        case _:
            return HFLLMModel(model_name=model_name, batch_size=batch_size)
