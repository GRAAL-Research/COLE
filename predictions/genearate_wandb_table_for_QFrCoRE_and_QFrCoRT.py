import os
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Optional

import pandas as pd
import wandb

from src import WANDB_PROJECT

PROJECT_PATH = f"doctorate/{WANDB_PROJECT}"
FULL_TABLE_CSV = os.path.join("results", "qfr_accuracy_table.csv")
FULL_TABLE_LATEX = os.path.join("results", "qfr_accuracy_table.tex")

TARGET_TASKS = {"qfrcore", "qfrcort"}


@dataclass
class ModelAttributes:
    phi_models: bool = False  # Φ
    gamma_models: bool = False  # Γ
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
        self.phi_models = {"chocolatine", "french-alpaca", "lucie"}

        self.size_patterns = {
            r"(\d+\.\d+)[bB]": r"$\1$B",
            r"(\d+\.\d+)[mM]": r"$\1$M",
        }

    def get_model_family(self, name: str) -> str:
        n = name.lower()
        if "gpt" in n:
            return "gpt"
        if "claude" in n:
            return "claude"
        if "gemini" in n:
            return "gemini"
        if "phi" in n:
            return "phi"
        if "deepseek" in n:
            return "deepseek"
        if "qwen" in n:
            return "qwen"
        if "llama" in n:
            return "llama"
        if "mistral" in n:
            return "mistral"
        if "gemma" in n:
            return "gemma"
        if "granite" in n:
            return "granite"
        if "aya" in n:
            return "aya"
        if "grok" in n:
            return "grok"
        if n.startswith(("o1", "o3", "o4")):
            return n.split("-")[0] if "-" in n else n[:2]
        return "unknown"

    def get_model_attributes(self, name: str) -> ModelAttributes:
        n = name.lower()
        gamma = any(p in n for p in self.gamma_models)
        phi = any(p in n for p in self.phi_models)
        if "french-alpaca" in n:
            phi = True
            gamma = True
        return ModelAttributes(
            phi_models=phi, gamma_models=gamma, model_family=self.get_model_family(name)
        )

    def normalize_base_name(self, name: str) -> str:
        n = name
        n = n.replace("-unsloth-bnb-4bit", "").replace("-bnb-4bit", "")
        n = re.sub(r"(?i)-instruct\b", "-it", n)

        # Capitalisation/normalisation des familles
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
        # Spéciaux
        n = re.sub(r"(?i)^meta-llama(?=-|$)", "Meta-Llama", n)
        n = re.sub(r"(?i)^s1\.1(?=-|$)", "S1.1", n)

        n = re.sub(r"(\d+\.\d+)", r"$\1$", n)

        for pattern, replacement in self.size_patterns.items():
            n = re.sub(pattern, replacement, n)

        return n

    def format_for_latex(self, name: str) -> str:
        attrs = self.get_model_attributes(name)
        normalized = self.normalize_base_name(name)
        formatted = r"\texttt{" + normalized + "}"
        symbols = []
        if attrs.gamma_models:
            symbols.append(r"$\Gamma$")
        if attrs.phi_models:
            symbols.append(r"$\Phi$")
        if symbols:
            formatted += " " + "".join(symbols)
        return formatted

    def process_model_name(self, name: str) -> str:
        return self.format_for_latex(name)


def main():
    os.makedirs("results", exist_ok=True)

    api = wandb.Api()
    runs = api.runs(PROJECT_PATH)

    processor = ModelNameProcessor()
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
                        # On convertit en pourcentage comme avant
                        results_by_model[model_display_name][col] = (
                            metrics[acc_key] * 100
                        )

    df = pd.DataFrame.from_dict(results_by_model, orient="index")
    df.index.name = "model_name"
    df.reset_index(inplace=True)

    df["model_name"] = df["model_name"].apply(processor.process_model_name)
    df = df.sort_values("model_name").reset_index(drop=True)

    os.makedirs(os.path.dirname(FULL_TABLE_CSV), exist_ok=True)
    df.to_csv(FULL_TABLE_CSV, index=False)

    for col in df.columns:
        if col != "model_name":
            df[col] = df[col].apply(
                lambda x: f"${x:.2f}$" if isinstance(x, (int, float)) else x
            )

    with open(FULL_TABLE_LATEX, "w", encoding="utf-8") as f:
        f.write(df.to_latex(index=False, escape=False))


if __name__ == "__main__":
    main()
