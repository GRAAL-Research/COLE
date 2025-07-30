from dotenv import dotenv_values

from src.model.model_factory import model_tokenizer_factory


def model_size(model_name: str):
    secrets = dotenv_values(".env")

    huggingface_token = secrets["huggingface_token"]

    model, _ = model_tokenizer_factory(
        model_name=(
            model_name
            if "_prompting" not in model_name
            else model_name.replace("_prompting", "")
        ),
        huggingface_token=huggingface_token,
    )

    num_params = model.num_parameters()

    return num_params
