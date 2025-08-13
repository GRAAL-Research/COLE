import os
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Optional

import pandas as pd
import wandb

from src import WANDB_PROJECT

PROJECT_PATH = f"doctorate/{WANDB_PROJECT}"
MODELS_SIZE_PATH = "models_size.json"
FULL_TABLE_CSV = os.path.join("results", "full_results_table.csv")
FULL_TABLE_LATEX = os.path.join("results", "full_results_table.tex")


@dataclass
class ModelAttributes:
    phi_models: bool = False
    gamma_models: bool = False
    special_formatting: Optional[str] = None
    model_family: Optional[str] = None


class ModelNameProcessor:
    """Handles model name normalization and attribute assignment."""

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
        if name_lower.startswith(("o1", "o3", "o4")):
            return name_lower.split("-")[0] if "-" in name_lower else name_lower[:2]
        return "unknown"

    def get_model_attributes(self, name: str) -> ModelAttributes:
        name_lower = name.lower()
        gamma_models = any(p in name_lower for p in self.gamma_models)
        phi_models = any(p in name_lower for p in self.phi_models)

        if "french-alpaca" in name_lower:
            phi_models = True
            gamma_models = True

        family = self.get_model_family(name)
        return ModelAttributes(
            phi_models=phi_models, gamma_models=gamma_models, model_family=family
        )

    def normalize_base_name(self, name: str) -> str:
        """Apply basic normalization to model name."""
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
        n = re.sub(r"(?i)^s1\.1(?=-|$)", "S1.1", n)

        n = re.sub(r"(\d+\.\d+)", r"$\1$", n)

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
        if attributes.phi_models:
            symbols.append(r"$\Phi$")
        if symbols:
            formatted += " " + "".join(symbols)
        return formatted

    def process_model_name(self, name: str, for_latex: bool = True) -> str:
        return (
            self.format_for_latex(name) if for_latex else self.normalize_base_name(name)
        )


def main():
    os.makedirs("results", exist_ok=True)
    api = wandb.Api()
    runs = api.runs(PROJECT_PATH)

    processor = ModelNameProcessor()
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
                                    results_by_model[model_display_name][key] = (
                                        value * 100
                                    )
                                    all_columns.add(key)

    sorted_columns = sorted(all_columns)
    df = pd.DataFrame.from_dict(
        results_by_model, orient="index", columns=sorted_columns
    )
    df.index.name = "model_name"
    df.reset_index(inplace=True)

    df["model_name"] = df["model_name"].apply(
        lambda x: processor.process_model_name(x, for_latex=True)
    )
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
    df.to_latex(FULL_TABLE_LATEX, index=False, float_format="%.2f", escape=False)

    print("Results saved to:")
    print(f"  CSV: {FULL_TABLE_CSV}")
    print(f"  LaTeX: {FULL_TABLE_LATEX}")

    print("\nSample processed model names:")
    for i, name in enumerate(df["model_name"].head(10)):
        print(f"  {i + 1}. {name}")


if __name__ == "__main__":
    main()
