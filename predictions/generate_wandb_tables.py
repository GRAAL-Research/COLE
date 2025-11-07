import os
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Optional, Dict, List

import pandas as pd
import wandb

from src import (
    WANDB_PROJECTS,
    NA_VALUE,
    COLE_TASKS,
    NEW_TASKS,
    TARGET_TASKS,
)

# Fichiers de sortie
FULL_TABLE_CSV = os.path.join("results", "full_results_table.csv")
FULL_TABLE_LATEX = os.path.join("results", "full_results_table.tex")

COLE_TABLE_CSV = os.path.join("results", "cole_results_table.csv")
COLE_TABLE_LATEX = os.path.join("results", "cole_results_table.tex")

NEW_TABLE_CSV = os.path.join("results", "new_results_table.csv")
NEW_TABLE_LATEX = os.path.join("results", "new_results_table.tex")


def _build_project_path(p: str) -> str:
    """Normalise le nom de projet W&B pour inclure l'entité si nécessaire."""
    if "/" in p:
        return p
    return f"doctorate/{p}"


PROJECT_PATHS: List[str] = [_build_project_path(p) for p in WANDB_PROJECTS]


@dataclass
class ModelAttributes:
    upsilon_models: bool = False
    gamma_models: bool = False
    special_formatting: Optional[str] = None
    model_family: Optional[str] = None


class ModelNameProcessor:
    """Utilitaire pour normaliser et formatter les noms de modèles (latex-friendly)."""

    def __init__(self) -> None:
        self.gamma_models = {
            "gpt-5",
            "o1",
            "o3",
            "o4",
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
            "grok-4",
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
        for family in [
            "gpt",
            "claude",
            "gemini",
            "phi",
            "deepseek",
            "qwen",
            "llama",
            "mistral",
            "gemma",
            "granite",
            "aya",
            "grok",
            "croissant",
        ]:
            if family in name_lower:
                return family
        if name_lower.startswith(("o1", "o3", "o4")):
            return name_lower.split("-")[0]
        return "unknown"

    def get_model_attributes(self, name: str) -> ModelAttributes:
        name_lower = name.lower()
        gamma_models = any(p in name_lower for p in self.gamma_models)
        upsilon_models = any(p in name_lower for p in self.upsilon_models)

        # cas particulier
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
        """Nettoie et normalise le nom brut du modèle (sans LaTeX)."""
        n = re.sub(r"(?i)-instruct\b", "-it", name)
        n = re.sub(r"(?i)-unsloth-bnb-4bit|-bnb-4bit", "", n)
        # Capitalise le préfixe alphabétique (simple mais suffisant ici)
        n = re.sub(r"(?i)^([a-zA-Z]+)", lambda m: m.group(1).capitalize(), n)
        # Formatage des tailles (M/B)
        for pattern, replacement in self.size_patterns.items():
            n = re.sub(pattern, replacement, n)
        return n

    def format_for_latex(self, name: str) -> str:
        """Retourne un nom formaté pour LaTeX, avec tags Γ / Υ si besoin."""
        attrs = self.get_model_attributes(name)
        formatted = r"\texttt{" + self.normalize_base_name(name) + "}"
        symbols = []
        if attrs.gamma_models:
            symbols.append(r"$\Gamma$")
        if attrs.upsilon_models:
            symbols.append(r"$\Upsilon$")
        if symbols:
            formatted += " (" + "".join(symbols) + ")"
        return formatted

    def process_model_name(self, name: str, for_latex: bool = True) -> str:
        return (
            self.format_for_latex(name) if for_latex else self.normalize_base_name(name)
        )


def _scale_if_fraction(x: float):
    """Si x est dans [0,1], on le traite comme un ratio et on le met en pourcentage."""
    try:
        v = float(x)
        return v * 100.0 if 0.0 <= v <= 1.001 else v
    except Exception:
        return x


def _task_in_target_list(task_name: str, targets: List[str]) -> bool:
    """Vérifie si une tâche (éventuellement avec chemin) est dans TARGET_TASKS."""
    if not targets:
        return True
    base = task_name.split("/")[-1]
    return base in targets


def _task_from_column(col: str) -> Optional[str]:
    """Récupère le nom de tâche à partir d'un nom de colonne."""
    if col in ("model_name", "Composite Score"):
        return None
    if " (" in col:
        return col.split(" (")[0]
    if col.endswith(" exact_match") or col.endswith(" f1"):
        return col.rsplit(" ", 1)[0]
    return col


def main() -> None:
    os.makedirs("results", exist_ok=True)
    api = wandb.Api()
    processor = ModelNameProcessor()

    results_by_model: Dict[str, Dict[str, float]] = defaultdict(dict)

    for project_path in PROJECT_PATHS:
        runs = api.runs(project_path)
        for run in runs:
            if run.state != "finished":
                continue

            summary = run.summary._json_dict
            config = run.config
            model_name = config.get("model_name", "unknown_model").split("/")[-1]

            tasks = summary.get("tasks")
            if not isinstance(tasks, list):
                continue

            for task_dict in tasks:
                for task_name, task_content in task_dict.items():
                    if not _task_in_target_list(task_name, TARGET_TASKS):
                        continue

                    for metrics in task_content.values():
                        if not isinstance(metrics, dict):
                            continue

                        if "exact_match" in metrics and "f1" in metrics:
                            em = _scale_if_fraction(metrics["exact_match"])
                            f1 = _scale_if_fraction(metrics["f1"])
                            key_em = f"{task_name} exact_match"
                            key_f1 = f"{task_name} f1"
                            results_by_model[model_name][key_em] = em
                            results_by_model[model_name][key_f1] = f1
                        else:
                            for m_name, val in metrics.items():
                                if isinstance(val, (float, int)):
                                    key = f"{task_name} ({m_name})"
                                    results_by_model[model_name][key] = (
                                        _scale_if_fraction(val)
                                    )

    df = pd.DataFrame.from_dict(results_by_model, orient="index")
    df["Composite Score"] = df.mean(axis=1)
    df.reset_index(inplace=True)
    df.rename(columns={"index": "model_name"}, inplace=True)

    df["model_name"] = df["model_name"].apply(
        lambda x: processor.process_model_name(x, for_latex=True)
    )

    cols = df.columns.tolist()
    ordered_cols: List[str] = []
    if "model_name" in cols:
        ordered_cols.append("model_name")
    if "Composite Score" in cols:
        ordered_cols.append("Composite Score")
    ordered_cols += [c for c in cols if c not in ("model_name", "Composite Score")]
    df = df[ordered_cols]

    df = df.fillna(NA_VALUE)

    df.to_csv(FULL_TABLE_CSV, index=False)
    df.drop("Composite Score", axis=1).to_latex(
        FULL_TABLE_LATEX,
        index=False,
        float_format="%.2f",
        escape=False,
    )

    cole_cols = [
        c
        for c in df.columns
        if _task_from_column(c) in COLE_TASKS or c in ("model_name", "Composite Score")
    ]
    df_cole = df[cole_cols]
    df_cole.to_csv(COLE_TABLE_CSV, index=False)
    df_cole.drop("Composite Score", axis=1).to_latex(
        COLE_TABLE_LATEX,
        index=False,
        float_format="%.2f",
        escape=False,
    )

    new_cols = [
        c
        for c in df.columns
        if _task_from_column(c) in NEW_TASKS or c in ("model_name", "Composite Score")
    ]
    df_new = df[new_cols]
    df_new.to_csv(NEW_TABLE_CSV, index=False)
    df_new.drop("Composite Score", axis=1).to_latex(
        NEW_TABLE_LATEX,
        index=False,
        float_format="%.2f",
        escape=False,
    )


if __name__ == "__main__":
    main()
