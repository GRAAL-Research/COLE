import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import json
import re
from typing import Dict, Optional

MODELS_SIZE_PATH = "models_size.json"


SIZE_RX = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*([BbMmKk]?)\s*$")


def parse_size(v) -> Optional[float]:
    """Convertit une taille JSON en float (B=1e9, M=1e6, K=1e3)."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        m = SIZE_RX.match(v)
        if not m:
            return None
        num = float(m.group(1))
        unit = m.group(2).upper()
        return num * (
            1e9 if unit == "B" else 1e6 if unit == "M" else 1e3 if unit == "K" else 1.0
        )
    return None


def strip_tex(name: str) -> str:
    r"""
    Supprime LaTeX: \texttt{...}, \Phi, \Gamma, \;, ~ et les $...$.
    (utilise des raw strings pour éviter les warnings d'escape)
    """
    n = str(name)
    n = re.sub(r"\\texttt\{", "", n)
    n = n.replace("}", "")
    n = n.replace(r"\Phi", "").replace(r"\Gamma", "").replace(r"\;", " ")
    n = n.replace("~", " ").replace("$", "")
    n = " ".join(n.split())
    return n.strip()


SUFFIX_RX = re.compile(
    r"(?:(?:-it)|(?:-bnb-4bit)|(?:-unsloth-bnb-4bit)|(?:-dpo-v[\d\.]+)|(?:-v[\d\.]+))+$",
    re.IGNORECASE,
)


def normalize_key(name: str) -> str:
    """
    Normalise pour lookup:
      - retire LaTeX
      - -instruct -> -it
      - retire suffixes (-it, -bnb-4bit, -dpo-vX, -vX…)
      - lower, espaces -> '-', compresse les '-'
    """
    n = strip_tex(name)
    n = re.sub(r"(?i)-instruct\b", "-it", n)
    n = n.lower().strip().replace(" ", "-")
    n = re.sub(SUFFIX_RX, "", n)
    n = re.sub(r"-+", "-", n)
    return n


def build_size_index(raw_size_dict: Dict[str, float | str]) -> Dict[str, float]:
    """
    Construit un index {normalized_key: size_float} à partir du JSON,
    ajoute aussi la clé 'org/model' -> 'model'.
    """
    idx: Dict[str, float] = {}
    for k, v in raw_size_dict.items():
        size = parse_size(v)
        if size is None:
            continue
        k1 = normalize_key(k)
        idx[k1] = size
        if "/" in k:
            k2 = normalize_key(k.split("/", 1)[-1])
            idx.setdefault(k2, size)
    return idx


def generate_size_vs_score_plot(
    csv_path: str,
    sizes_json_path: str = MODELS_SIZE_PATH,
    output_path: str = "results/model_size_vs_score.png",
) -> None:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"File {csv_path} not found. Please check the path.")

    df = pd.read_csv(csv_path)

    if not os.path.exists(sizes_json_path):
        raise FileNotFoundError(
            f"File {sizes_json_path} not found. Please check the path."
        )
    with open(sizes_json_path, "r", encoding="utf-8") as f:
        size_dict = json.load(f)

    size_index = build_size_index(size_dict)

    model_col = (
        "model_name"
        if "model_name" in df.columns
        else ("model" if "model" in df.columns else None)
    )
    if model_col is None:
        raise KeyError(f"No 'model_name' or 'model' column in CSV: {list(df.columns)}")

    df["_lookup_key"] = df[model_col].astype(str).map(normalize_key)

    df["model_size"] = df["_lookup_key"].map(size_index)

    missing = df[df["model_size"].isna()]["_lookup_key"].unique()
    for key in missing:
        parts = key.split("-")
        prefix = "-".join(parts[:2]) if len(parts) > 1 else key
        cand = [
            k
            for k in size_index
            if k == prefix or k.startswith(prefix) or prefix.startswith(k)
        ]
        if cand:
            df.loc[df["_lookup_key"] == key, "model_size"] = size_index[cand[0]]

    still_missing = df[df["model_size"].isna()]["_lookup_key"].unique()
    for key in still_missing:
        cand = [k for k in size_index if key in k or k in key]
        if cand:
            df.loc[df["_lookup_key"] == key, "model_size"] = size_index[cand[0]]

    em_f1_cols = [
        c for c in df.columns if "(exact match, f1)" in c or "(exact_match/f1)" in c
    ]
    for col in em_f1_cols:
        base = col.split(" (")[0]
        split = df[col].astype(str).str.split("/", expand=True)
        df[[f"{base}_exact", f"{base}_f1"]] = split.astype(float)
    if em_f1_cols:
        df.drop(columns=em_f1_cols, inplace=True)

    for c in df.columns:
        if (
            "(accuracy)" in c
            and pd.api.types.is_numeric_dtype(df[c])
            and df[c].max() <= 1.0
        ):
            df[c] = df[c] * 100.0

    exclude = {model_col, "_lookup_key", "model_size"}
    metrics = [
        c for c in df.select_dtypes(include=[np.number]).columns if c not in exclude
    ]

    df["mean_score"] = df[metrics].mean(axis=1)

    baseline_row = df[df["_lookup_key"] == normalize_key("RandomBaselineModel")]
    baseline_score = (
        baseline_row[metrics].mean(axis=1).iloc[0] if not baseline_row.empty else None
    )

    dropped_no_size = df[df["model_size"].isna()][model_col].tolist()
    dropped_no_metric = df[df["mean_score"].isna()][model_col].tolist()
    if dropped_no_size:
        print(
            f"[WARN] {len(dropped_no_size)} modèles sans taille trouvée (ignorés): {dropped_no_size[:10]}{' ...' if len(dropped_no_size)>10 else ''}"
        )
    if dropped_no_metric:
        print(
            f"[WARN] {len(dropped_no_metric)} modèles sans métriques numériques (ignorés): {dropped_no_metric[:10]}{' ...' if len(dropped_no_metric)>10 else ''}"
        )

    df = df[df["model_size"].notna() & df["mean_score"].notna()].copy()
    df.sort_values(by=model_col, inplace=True)
    if df.empty:
        raise RuntimeError(
            "No data to plot after filtering (check size mapping and metrics)."
        )

    X = np.log10(df["model_size"].astype(float).values)
    Y = df["mean_score"].astype(float).values
    slope, intercept = np.polyfit(X, Y, 1)
    line = slope * X + intercept

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.figure(figsize=(10, 6))
    plt.scatter(df["model_size"], df["mean_score"], label="Models")
    plt.plot(df["model_size"], line, label="Linear regression")

    if baseline_score is not None:
        plt.axhline(
            baseline_score,
            linestyle="--",
            color="red",
            label=f"Baseline ({baseline_score:.2f}%)",
        )

    plt.xscale("log")
    plt.xlabel("Model size (log scale)")
    plt.ylabel("Average score (%)")
    plt.title("Model size vs performance")
    plt.grid(True, which="both", axis="both")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


if __name__ == "__main__":
    generate_size_vs_score_plot("results/full_results_table.csv")
