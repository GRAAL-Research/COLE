import os
import pandas as pd
from collections import defaultdict
import wandb

PROJECT_PATH = "doctorate/COLE"
MODELS_SIZE_PATH = "models_size.json"
FULL_TABLE_CSV = "results/full_results_table.csv"
FULL_TABLE_LATEX = "results/full_results_table.tex"


def main():
    os.makedirs("results", exist_ok=True)

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

        if "tasks" in summary and isinstance(summary["tasks"], list):
            for task_dict in summary["tasks"]:
                for task_name, task_content in task_dict.items():
                    for metrics in task_content.values():
                        if "exact_match" in metrics and "f1" in metrics:
                            em = metrics["exact_match"]
                            f1 = metrics["f1"]
                            key = f"{task_name} (exact_match/f1)"
                            results_by_model[model_display_name][
                                key
                            ] = f"{em:.3f}/{f1:.3f}"
                            all_columns.add(key)
                        else:
                            for metric_name, value in metrics.items():
                                if isinstance(value, (float, int)):
                                    key = f"{task_name} ({metric_name})"
                                    results_by_model[model_display_name][key] = value
                                    all_columns.add(key)

    sorted_columns = sorted(all_columns)
    df = pd.DataFrame.from_dict(
        results_by_model, orient="index", columns=sorted_columns
    )
    df.index.name = "model_name"
    df.reset_index(inplace=True)
    df["model_name"] = df["model_name"].str.replace(
        "-unsloth-bnb-4bit", "", regex=False
    )
    df["model_name"] = df["model_name"].str.replace("-bnb-4bit", "", regex=False)
    df["model_name"] = df["model_name"].str.replace("Instruct", "it", regex=False)
    df = df.sort_values("model_name").reset_index(drop=True)

    combined_cols = [
        col
        for col in df.columns
        if df[col].dtype == object and df[col].astype(str).str.contains("/").any()
    ]
    for col in combined_cols:
        base = col.split(" (")[0]
        em_vals, f1_vals = df[col].str.split("/", expand=True).astype(float).T.values
        df[f"{base} exact_match"] = em_vals
        df[f"{base} f1"] = f1_vals
        df.drop(columns=[col], inplace=True)

    df.to_csv(FULL_TABLE_CSV, index=False)
    df.to_latex(FULL_TABLE_LATEX, index=False, float_format="%.3f")


if __name__ == "__main__":
    main()
