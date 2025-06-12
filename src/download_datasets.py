# This script downloads all the Colle Benchmarks to a local directory, defaults to ./Benchmarks
# It also provides utility methods to fetch all datasets from a local directory or from the online huggingFace Dataset
import os

import huggingface_hub
from datasets import load_dataset
from huggingface_hub import snapshot_download
from dotenv import load_dotenv


load_dotenv()

REPO_ID = "COLLE-Graal/ColleGraal"
DATA_DIRECTORY = "data"
DIRECTORY = "./Benchmarks"
HF_TOKEN = os.getenv('HF_TOKEN')

datasets = ["Allocine", "paws_x", "fquad", "opus_parcus", "gqnli", "multiblimp", "piaf", "sickfr", "Xnli"]

huggingface_hub.login(token=HF_TOKEN)


def download_datasets():
    snapshot_download(repo_id=REPO_ID, local_dir=DIRECTORY, allow_patterns=f"*.jsonl", repo_type="dataset")


def load_datasets_from_disk(directory=DIRECTORY):
    data = dict()
    print(f"Loading datasets from {os.path.realpath(directory + "/" + DATA_DIRECTORY)}...")
    for dataset_name in datasets:
        try:
            data[dataset_name] = load_dataset_from_disk(dataset_name, directory)
        except Exception as e:
            print(
                f"{dataset_name} dataset was not able to be loaded, please ensure that datasets were retrieved with download_datasets()")

    return data


def load_dataset_from_disk(dataset_name, directory=DIRECTORY):
    path = directory + "/" + DATA_DIRECTORY + "/" + dataset_name

    new_dataset = load_dataset(path)
    return new_dataset


def load_datasets_from_huggingface():
    data = dict()
    print(f"Loading datasets from {REPO_ID}/{DATA_DIRECTORY}...")
    for dataset_name in datasets:
        new_dataset = load_dataset_from_huggingface(dataset_name)
        data[dataset_name] = new_dataset

    return data


def load_dataset_from_huggingface(dataset_name,split=None):
    try:
        hub_dir = f"{DATA_DIRECTORY}/{dataset_name}"
        if split is None :
           new_dataset = load_dataset(REPO_ID, data_dir=hub_dir)
        else:
            new_dataset = load_dataset(REPO_ID, data_dir=hub_dir,split=split)
        return new_dataset
    except Exception as e:
        print(f"{dataset_name} dataset was not able to be loaded, {e}. Please ensure that datasets names fit with names on the hub.")
        return None
