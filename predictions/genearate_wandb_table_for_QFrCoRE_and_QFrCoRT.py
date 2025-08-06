import os
import pandas as pd
from collections import defaultdict
import wandb

PROJECT_PATH = "doctorate/COLE"
FULL_TABLE_CSV = "results/qfr_accuracy_table.csv"
FULL_TABLE_LATEX = "results/qfr_accuracy_table.tex"

TARGET_TASKS = {"qfrcore", "qfrcort"}


def main():
    os.makedirs("results", exist_ok=True)

    api = wandb.Api()
    runs = api.runs(PROJECT_PATH)

    results_by_model = defaultdict(dict)

    for run in runs:
        if run.state != "finished":
            continue

        summary = run.summary._json_dict
        config = run.config
        full_model_name = config.get("model_name", "unknown_model")
        model_display_name = full_model_name.split("/")[-1]

        tasks = summary.get("tasks")
        if not isinstance(tasks, list):
            continue

        for task_dict in tasks:
            if not isinstance(task_dict, dict):
                continue
            for task_name, task_content in task_dict.items():
                if task_name not in TARGET_TASKS or not isinstance(task_content, dict):
                    continue

                for metrics in task_content.values():
                    if not isinstance(metrics, dict):
                        continue
                    if "accuracy" in metrics or "acc" in metrics:
                        acc_key = "accuracy" if "accuracy" in metrics else "acc"
                        col = f"{task_name} accuracy"
                        results_by_model[model_display_name][col] = metrics[acc_key] * 100

    df = pd.DataFrame.from_dict(results_by_model, orient="index")
    df.index.name = "model_name"
    df.reset_index(inplace=True)

    df["model_name"] = (
        df["model_name"]
        .astype(str)
        .str.replace("-unsloth-bnb-4bit", "", regex=False)
        .str.replace("-bnb-4bit", "", regex=False)
        .str.replace("Instruct", "it", regex=False)
    )

    df = df.sort_values("model_name").reset_index(drop=True)

    os.makedirs(os.path.dirname(FULL_TABLE_CSV), exist_ok=True)
    df.to_csv(FULL_TABLE_CSV, index=False)
    df.to_latex(FULL_TABLE_LATEX, index=False, float_format="%.2f")


if __name__ == "__main__":
    main()
