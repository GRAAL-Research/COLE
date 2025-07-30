import json

from tqdm import tqdm

from predictions.all_llms import llms
from predictions.model_size import model_size

if __name__ == "__main__":

    model_names = llms["all"]

    # We create a new model JSON file to write the number of params.
    with open("models_size.json", "w", encoding="utf-8") as file:
        json.dump({}, file, ensure_ascii=False)

    for model_name in tqdm(model_names):
        num_params = model_size(model_name)

        # We load the file to append the new datapoint to it.
        with open("models_size.json", "r", encoding="utf-8") as file:
            models_size = json.load(file)

        models_size.update({model_name: num_params})

        # We dump the models_size
        with open("models_size.json", "w", encoding="utf-8") as file:
            json.dump(models_size, file, ensure_ascii=False)
