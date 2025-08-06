import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import json
import re

MODELS_SIZE_PATH = "models_size.json"


def generate_size_vs_score_plot(
    csv_path: str,
    sizes_json_path: str = MODELS_SIZE_PATH,
    output_path: str = "results/model_size_vs_score.png",
) -> None:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f" File {csv_path} not found. Please check the path.")

    df = pd.read_csv(csv_path)

    if not os.path.exists(sizes_json_path):
        raise FileNotFoundError(
            f" File {sizes_json_path} not found. Please check the path."
        )
    with open(sizes_json_path, "r") as f:
        size_dict = json.load(f)

    stripped_dict = {k.split("/", 1)[-1]: v for k, v in size_dict.items()}

    model_col = "model_name" if "model_name" in df.columns else "model"
    if model_col not in df.columns:
        raise KeyError(f" No 'model_name' or 'model' column in CSV: {list(df.columns)}")

    df[model_col] = df[model_col].str.replace("Instruct", "it", regex=False)

    df["model_size"] = (
        df[model_col].map(size_dict).fillna(df[model_col].map(stripped_dict))
    )

    suffix_pat = r"(?:(?:-it)|(?:-bnb-4bit)|(?:-unsloth-bnb-4bit)|(?:-DPO-v[\d\.]+)|(?:-v[\d\.]+))+$"
    missing = df[df["model_size"].isna()][model_col].unique()
    for name in missing:
        base = re.sub(suffix_pat, "", name)
        parts = base.split("-")
        prefix = f"{parts[0]}-{parts[1]}" if len(parts) > 1 else base
        candidates = [
            k for k in stripped_dict if prefix == k or prefix in k or k in prefix
        ]
        if candidates:
            df.loc[df[model_col] == name, "model_size"] = stripped_dict[candidates[0]]

    missing = df[df["model_size"].isna()][model_col].unique()
    for name in missing:
        candidates = [
            k
            for k in stripped_dict
            if k.startswith(name) or name.startswith(k) or name in k or k in name
        ]
        if candidates:
            df.loc[df[model_col] == name, "model_size"] = stripped_dict[candidates[0]]

    em_f1 = [c for c in df.columns if "(exact match, f1)" in c]
    for col in em_f1:
        base = col.split(" (")[0]
        df[[f"{base}_exact", f"{base}_f1"]] = (
            df[col].str.split("/", expand=True).astype(float)
        )
    df.drop(columns=em_f1, inplace=True)

    for c in df.columns:
        if "(accuracy)" in c and df[c].max() <= 1.0:
            df[c] = df[c] * 100

    exclude = [model_col, "model_size"]
    metrics = [
        c for c in df.select_dtypes(include=[np.number]).columns if c not in exclude
    ]

    df["mean_score"] = df[metrics].mean(axis=1)

    baseline_row = df[df[model_col] == "RandomBaselineModel"]
    if not baseline_row.empty:
        baseline_score = baseline_row[metrics].mean(axis=1).iloc[0]
    else:
        baseline_score = None

    df = df[df["model_size"].notna()]
    df.sort_values(by=model_col, inplace=True)

    X = np.log10(df["model_size"])
    Y = df["mean_score"]
    slope, intercept = np.polyfit(X, Y, 1)
    line = slope * X + intercept

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.figure(figsize=(10, 6))
    plt.scatter(df["model_size"], df["mean_score"], color="#1f77b4", label="Models")
    plt.plot(df["model_size"], line, color="#0057a3", label="Linear regression")

    if baseline_score is not None:
        print(f"✅ Baseline (RandomBaselineModel) score: {baseline_score:.2f}%")
        plt.axhline(
            baseline_score,
            linestyle="--",
            color="#87CEEB",
            label="Baseline (RandomBaselineModel)",
        )

    plt.xscale("log")
    plt.xlabel("Model size (log scale)")
    plt.ylabel("Average score (%)")
    plt.title("Model size vs performance")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


if __name__ == "__main__":
    generate_size_vs_score_plot("results/full_results_table.csv")
