import os
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Optional

import pandas as pd
import wandb

from predictions.all_llms import llms, small_llm, small_llm_2, private_llm
from src import WANDB_PROJECT

PROJECT_PATH = f"doctorate/{WANDB_PROJECT}"
MODELS_SIZE_PATH = "models_size.json"
FULL_TABLE_CSV = os.path.join("results", "full_results_table.csv")
FULL_TABLE_LATEX = os.path.join("results", "full_results_table.tex")
FULL_TABLE_CSV_short = os.path.join("results", "full_results_table_short.csv")
FULL_TABLE_LATEX_short = os.path.join("results", "full_results_table_short.tex")


@dataclass
class ModelAttributes:
    upsilon_models: bool = False
    gamma_models: bool = False
    special_formatting: Optional[str] = None
    model_family: Optional[str] = None


class ModelNameProcessor:
    def __init__(self):
        self.gamma_models = {
            "gpt-5",
            "o1",
            "o3",
            "o4",
            "gpt-oss",
            "claude-opus",
            "claude-sonnet",
            "gemini-2.5-pro",
            "deepseek-reasoner",
            "deepseek-r1-distill",
            "deepthink-reasoning",
            "grok-3",
            "mistral-large-latest",
            "reka-flash-3",
            "s1.1",
            "qwq",
            "llama-3.2",
            "meta-llama-3.1",
            "gemma-2",
        }
        self.upsilon_models = {
            "chocolatine",
            "french-alpaca",
            "lucie",
            "croissantllmbase",
        }
        self.size_patterns = {
            r"(\d+\.\d+)[bB]": r"$\1$B",
            r"(\d+\.\d+)[mM]": r"$\1$M",
        }

    def get_model_family(self, name: str) -> str:
        name_lower = name.lower()
        if "gpt" in name_lower:
            return "gpt"
        if "claude" in name_lower:
            return "claude"
        if "gemini" in name_lower:
            return "gemini"
        if "phi" in name_lower:
            return "phi"
        if "deepseek" in name_lower:
            return "deepseek"
        if "qwen" in name_lower:
            return "qwen"
        if "llama" in name_lower:
            return "llama"
        if "mistral" in name_lower:
            return "mistral"
        if "gemma" in name_lower:
            return "gemma"
        if "granite" in name_lower:
            return "granite"
        if "aya" in name_lower:
            return "aya"
        if "grok" in name_lower:
            return "grok"
        if "croissant" in name_lower:
            return "Croissant"
        if name_lower.startswith(("o1", "o3", "o4")):
            return name_lower.split("-")[0] if "-" in name_lower else name_lower[:2]
        return "unknown"

    def get_model_attributes(self, name: str) -> ModelAttributes:
        name_lower = name.lower()
        gamma_models = any(p in name_lower for p in self.gamma_models)
        upsilon_models = any(p in name_lower for p in self.upsilon_models)
        if "french-alpaca" in name_lower:
            upsilon_models = True
            gamma_models = True
        family = self.get_model_family(name)
        return ModelAttributes(
            upsilon_models=upsilon_models,
            gamma_models=gamma_models,
            model_family=family,
        )

    def normalize_base_name(self, name: str) -> str:
        n = name
        n = n.replace("-unsloth-bnb-4bit", "").replace("-bnb-4bit", "")
        n = re.sub(r"(?i)-instruct\b", "-it", n)
        n = re.sub(r"(?i)^gpt(?=-|$)", "GPT", n)
        n = re.sub(r"(?i)^gemma(?=-|$)", "Gemma", n)
        n = re.sub(r"(?i)^gemini(?=-|$)", "Gemini", n)
        n = re.sub(r"(?i)^aya(?=-|$)", "Aya", n)
        n = re.sub(r"(?i)^granite(?=-|$)", "Granite", n)
        n = re.sub(r"(?i)^phi(?=-|$)", "Phi", n)
        n = re.sub(r"(?i)^reka-flash(?=-|$)", "Reka-flash", n)
        n = re.sub(r"(?i)^deepseek(?=-|$)", "DeepSeek", n)
        n = re.sub(r"(?i)^qwen(?=-|$)", "Qwen", n)
        n = re.sub(r"(?i)^llama(?=-|$)", "Llama", n)
        n = re.sub(r"(?i)^mistral(?=-|$)", "Mistral", n)
        n = re.sub(r"(?i)^claude(?=-|$)", "Claude", n)
        n = re.sub(r"(?i)^grok(?=-|$)", "Grok", n)
        n = re.sub(r"(?i)^olmo(?=-|$)", "OLMo", n)
        n = re.sub(r"(?i)^smollm(?=-|$)", "SmolLM", n)
        n = re.sub(r"(?i)^chocolatine(?=-|$)", "Chocolatine", n)
        n = re.sub(r"(?i)^french-alpaca(?=-|$)", "French-Alpaca", n)
        n = re.sub(r"(?i)^lucie(?=-|$)", "Lucie", n)
        n = re.sub(r"(?i)^deepthink(?=-|$)", "Deepthink", n)
        n = re.sub(r"(?i)^ministral(?=-|$)", "Ministral", n)
        n = re.sub(r"(?i)^mixtral(?=-|$)", "Mixtral", n)
        n = re.sub(r"(?i)^pixtral(?=-|$)", "Pixtral", n)
        n = re.sub(r"(?i)^qwq(?=-|$)", "QwQ", n)
        n = re.sub(r"(?i)^meta-llama(?=-|$)", "Meta-Llama", n)
        n = re.sub(r"(?i)^command(?=-|$)", "Command", n)
        n = re.sub(r"(?i)^c4ai-aya-expanse(?=-|$)", "C4ai-Aya-expanse", n)
        n = re.sub(r"(?i)^s1\.1(?=-|$)", "S1.1", n)
        n = re.sub(r"(\d+\.\d+\.?\d?)", r"$\1$", n)
        for pattern, replacement in self.size_patterns.items():
            n = re.sub(pattern, replacement, n)
        return n

    def format_for_latex(self, name: str) -> str:
        attributes = self.get_model_attributes(name)
        normalized = self.normalize_base_name(name)
        formatted = r"\texttt{" + normalized + "}"
        symbols = []
        if attributes.gamma_models:
            symbols.append(r"$\Gamma$")
        if attributes.upsilon_models:
            symbols.append(r"$\Upsilon$")
        if symbols:
            formatted += " (" + "".join(symbols) + ")"
        return formatted

    def process_model_name(self, name: str, for_latex: bool = True) -> str:
        return (
            self.format_for_latex(name) if for_latex else self.normalize_base_name(name)
        )


def _scale_if_fraction(x: float) -> float:
    if x is None:
        return x
    try:
        if 0.0 <= float(x) <= 1.001:
            return float(x) * 100.0
        return float(x)
    except Exception:
        return x


def main():
    os.makedirs("results", exist_ok=True)
    api = wandb.Api()
    runs = api.runs(PROJECT_PATH)

    processor = ModelNameProcessor()
    results_by_model = defaultdict(dict)
    all_columns = []
    all_model_names = []

    for run in runs:
        if run.state != "finished":
            continue
        summary = run.summary._json_dict
        config = run.config
        full_model_name = config.get("model_name", "unknown_model")
        all_model_names.append(full_model_name)
        model_display_name = full_model_name.split("/")[-1]

        if "tasks" in summary and isinstance(summary["tasks"], list):
            for task_dict in summary["tasks"]:
                for task_name, task_content in task_dict.items():
                    for metrics in task_content.values():
                        if "exact_match" in metrics and "f1" in metrics:
                            em = _scale_if_fraction(metrics["exact_match"])
                            f1 = _scale_if_fraction(metrics["f1"])
                            key_em = f"{task_name} exact_match"
                            key_f1 = f"{task_name} f1"
                            results_by_model[model_display_name][key_em] = em
                            results_by_model[model_display_name][key_f1] = f1
                            if key_em not in all_columns:
                                all_columns.extend([key_em, key_f1])
                        else:
                            for metric_name, value in metrics.items():
                                if isinstance(value, (float, int)):
                                    key = f"{task_name} ({metric_name})"
                                    results_by_model[model_display_name][key] = (
                                        float(value) * 100.0
                                    )
                                    if key not in all_columns:
                                        all_columns.append(key)

    print(
        set(
            llms["all"] + small_llm["all"] + small_llm_2["all"] + private_llm["all"]
        ).difference(set(all_model_names))
    )
    df = pd.DataFrame.from_dict(results_by_model, orient="index", columns=all_columns)
    df["Composite Score"] = df.mean(axis=1)
    df.index.name = "model_name"
    df.reset_index(inplace=True)
    df["model_name"] = df["model_name"].apply(
        lambda x: processor.process_model_name(x, for_latex=True)
    )
    df = df.sort_values("model_name").reset_index(drop=True)

    def sort_key(col: str):
        if col == "model_name":
            return ("", -1, "")
        task = col.split(" (")[0].split(" ")[0]
        if col.endswith(" exact_match"):
            kind = 0
        elif col.endswith(" f1"):
            kind = 1
        else:
            kind = 2
        return (task, kind, col)

    ordered_cols = sorted([c for c in df.columns], key=sort_key)
    df = df[ordered_cols]

    df.to_csv(FULL_TABLE_CSV, index=False)
    df = df.fillna(0.00)
    df.drop("Composite Score", axis=1).to_latex(FULL_TABLE_LATEX, index=False, float_format="%.2f", escape=False)

    df_sorted = (
        df[["model_name", "Composite Score"]]
        .sort_values("Composite Score", ascending=False)
        .reset_index(drop=True)
    )
    top_n = int(len(df_sorted) / 2)
    left = df_sorted.iloc[:top_n].reset_index(drop=True)
    right = df_sorted.iloc[top_n : ].reset_index(drop=True)
    right = right.reindex(range(len(left)))
    right["model_name"] = right["model_name"].fillna("")

    df_2 = pd.DataFrame(
        {
            "model_name": left["model_name"],
            "Composite Score": left["Composite Score"],
            "model_name_2": right["model_name"],
            "Composite Score_2": right["Composite Score"],
        }
    )

    df_2.to_latex(
        FULL_TABLE_LATEX_short, index=False, float_format="%.2f", escape=False
    )


if __name__ == "__main__":
    main()
