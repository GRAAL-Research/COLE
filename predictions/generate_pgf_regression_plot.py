import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os


def generate_size_vs_score_plot(
    csv_path: str, output_path: str = "results/model_size_vs_score.png"
) -> None:

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"❌ File {csv_path} not found. Please check the path.")

    df = pd.read_csv(csv_path)
    df = df[df["model_size"].notna()]

    for col in df.columns:
        if "(exact match, f1)" in col:
            base = col.split(" (")[0]
            df[[f"{base}_exact", f"{base}_f1"]] = (
                df[col].str.split("/", expand=True).astype(float)
            )

    df = df.drop(columns=[col for col in df.columns if "(exact match, f1)" in col])

    for col in df.columns:
        if "(accuracy)" in col and df[col].max() <= 1.0:
            df[col] = df[col] * 100

    exclude_cols = ["model_name", "model_size"]
    metric_cols = [
        col
        for col in df.select_dtypes(include=[float, int]).columns
        if col not in exclude_cols
    ]
    df["mean_score"] = df[metric_cols].mean(axis=1)

    X = np.log10(df["model_size"].values)
    Y = df["mean_score"].values
    slope, intercept = np.polyfit(X, Y, deg=1)
    regression_line = slope * X + intercept

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    plt.figure(figsize=(10, 6))
    plt.scatter(df["model_size"], df["mean_score"], color="blue", label="Models")
    plt.plot(
        df["model_size"],
        regression_line,
        color="green",
        linewidth=2,
        label="Linear regression",
    )
    plt.axhline(y=50, color="red", linestyle="--", label="Baseline")

    plt.xscale("log")
    plt.xlabel("Model size (log)")
    plt.ylabel("Average score (%)")
    plt.title("Model size vs average performance")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


if __name__ == "__main__":
    generate_size_vs_score_plot("results/full_results_table.csv")
