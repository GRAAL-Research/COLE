import json
import subprocess

from tqdm import tqdm

from predictions.all_llms import llms

model_names = llms["all"]

# We create a new model JSON file to write the number of params.
with open("models_size.json", "w", encoding="utf-8") as file:
    json.dump({}, file, ensure_ascii=False)

for model_name in tqdm(model_names):
    subprocess.run(
        f"python3 get_model_size.py {model_name}",
        shell=True,
    )
