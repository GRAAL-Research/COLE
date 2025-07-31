import os
import json
import pandas as pd
from collections import defaultdict
import wandb

PROJECT_PATH = "doctorate/COLLE"
MODELS_SIZE_PATH = "models_size.json"
EXPORT_CSV_PATH = "results/full_results_table.csv"
EXPORT_LATEX_PATH = "results/full_results_table.tex"

with open(MODELS_SIZE_PATH, "r", encoding="utf-8") as f:
    model_sizes = json.load(f)

api = wandb.Api()
runs = api.runs(PROJECT_PATH)

results_by_model = defaultdict(dict)
all_columns = set()

for run in runs:
    if run.state != "finished":
        continue

    summary = run.summary._json_dict
    config = run.config
    full_model_name = config.get("model_name", "unknown_model")
    model_display_name = full_model_name.split("/")[-1]

    task_data = {}

    if "tasks" in summary and isinstance(summary["tasks"], list):
        for task_dict in summary["tasks"]:
            for task_name, task_content in task_dict.items():
                for subtask_name, metrics in task_content.items():
                    if "exact_match" in metrics and "f1" in metrics:
                        em = metrics["exact_match"]
                        f1 = metrics["f1"]
                        display_key = f"{task_name} (exact match, f1)"
                        task_data[display_key] = f"{em:.3f}/{f1:.3f}"
                        all_columns.add(display_key)
                    else:
                        for metric_name, value in metrics.items():
                            if isinstance(value, (float, int)):
                                display_key = f"{task_name} ({metric_name})"
                                task_data[display_key] = value
                                all_columns.add(display_key)

    results_by_model[model_display_name] = task_data

sorted_columns = sorted(all_columns)
df = pd.DataFrame.from_dict(results_by_model, orient="index", columns=sorted_columns)
df.index.name = "model_name"
df.reset_index(inplace=True)


def find_model_size(model_display_name):
    for full_name, size in model_sizes.items():
        if full_name.endswith(model_display_name):
            return size
    return None


df["model_size"] = df["model_name"].map(find_model_size)

ordered_cols = ["model_name"] + sorted_columns + ["model_size"]
df = df[ordered_cols]


os.makedirs("results", exist_ok=True)
df.to_csv(EXPORT_CSV_PATH, index=False)
df.to_latex(EXPORT_LATEX_PATH, index=False, float_format="%.2f")
