import argparse
import json
import os
import re
from collections import defaultdict
from collections.abc import Mapping

import wandb
from cole import cole as project

# === Config par défaut ===
PROJECT_PATH = f"doctorate/{project}"
DEFAULT_OUT = "results/leaderboard.json"


TASK_METRICS = {
    "allocine": ["accuracy"],
    "piaf": ["exact_match", "f1"],
    "qfrcola": ["accuracy"],
    "gqnli": ["accuracy"],
    "xnli": ["accuracy"],
    "paws_x": ["accuracy"],
    "frblimp": ["accuracy"],
    "qfrblimp": ["accuracy"],
    "sts22": ["accuracy"],
    "sickfr": ["accuracy"],
    "fquad": ["f1", "exact_match"],
    "french_boolq": ["accuracy"],
    "daccord": ["accuracy"],
    "wino_x_lm": ["accuracy"],
    "wino_x_mt": ["accuracy"],
    "rte3-french": ["accuracy"],
    "mnli-nineeleven-fr-mt": ["accuracy"],
    "qfrcore": ["accuracy"],
    "qfrcort": ["accuracy"],
    "fracas": ["accuracy"],
    "lingnli": ["accuracy"],
    "mms": ["accuracy"],
    "multiblimp": ["accuracy"],
    "wsd": ["exact_match"],
}

CANDIDATE_PREFIXES = ["", "results.", "metrics.", "eval.", "evaluation.", "scores."]
SEPARATORS = ["/", ".", "_", "-"]


def norm(s):
    return str(s).lower().replace(" ", "_")


def canon(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


def flatten_dict(d, parent_key=""):
    items = {}
    for k, v in (d or {}).items():
        new_key = f"{parent_key}.{k}" if parent_key else str(k)
        if isinstance(v, Mapping):
            items.update(flatten_dict(v, new_key))
        else:
            items[new_key] = v
    return items


def find_value(summary, task, metric):
    """Recherche la valeur d’un metric pour une tâche donnée."""
    flat = flatten_dict(summary)
    candidates = []
    for pref in CANDIDATE_PREFIXES:
        for sep in SEPARATORS:
            candidates.append(f"{pref}{task}{sep}{metric}")
    candidates.extend([f"{task}.{metric}", f"{metric}.{task}"])
    cand_set = {norm(c) for c in candidates}
    for k, v in flat.items():
        if norm(k) in cand_set:
            return v
    c_task = canon(task)
    c_metric = canon(metric)
    for k, v in flat.items():
        if not isinstance(v, (int, float, str)):
            continue
        ck = canon(k)
        if c_task in ck and c_metric in ck:
            return v
    return None


def extract_tasks(summary):
    out = {}
    for task, metrics in TASK_METRICS.items():
        task_block = {}
        for m in metrics:
            val = find_value(summary, task, m)
            try:
                if val is not None:
                    val_f = float(val)
                    if 0.0 <= val_f <= 1.001:
                        val_f *= 100.0
                    task_block[m] = val_f
            except Exception:
                pass
        if task_block:
            out[task] = task_block
    return out


def best_model_url(model_name):
    if not model_name:
        return None
    if re.match(r"^[\w-]+/[\w.-]+$", model_name):
        return f"https://huggingface.co/{model_name}"
    return None


def run_to_record(run, override_name=None, override_url=None):
    cfg = run.config or {}
    summ = run.summary or {}
    name = (
        override_name
        or cfg.get("model_name")
        or summ.get("model_name")
        or cfg.get("model")
        or run.name
    )
    url = (
        override_url
        or cfg.get("model_url")
        or summ.get("model_url")
        or best_model_url(name)
    )
    tasks = extract_tasks(summ)
    if not tasks:
        hist = run.history(samples=2000)
        merged = {}
        for col in hist.columns:
            lc = norm(col)
            for task in TASK_METRICS:
                for sep in SEPARATORS:
                    if (
                        lc.startswith(task + sep)
                        or lc.endswith(sep + task)
                        or (sep + task + sep) in lc
                    ):
                        merged[col] = hist[col].dropna().iloc[-1]
                        break
        if merged:
            tasks = extract_tasks(merged)
    tasks_list = [{t: tasks[t]} for t in sorted(tasks.keys())]
    return {"model_name": name, "model_url": url, "tasks": tasks_list}


def primary_metric_value(task_block):
    if not task_block:
        return None
    keys = list(task_block.keys())
    return task_block[keys[0]]


def merge_by_model(records):
    grouped = defaultdict(list)
    for r in records:
        grouped[r["model_name"]].append(r)
    merged = []
    for name, recs in grouped.items():
        combined = {"model_name": name, "model_url": None, "tasks": []}
        task_map = {}
        for r in recs:
            if not combined["model_url"] and r.get("model_url"):
                combined["model_url"] = r["model_url"]
            for item in r["tasks"]:
                [(task, vals)] = list(item.items())
                if task not in task_map:
                    task_map[task] = vals
                else:
                    v_new = primary_metric_value(vals)
                    v_old = primary_metric_value(task_map[task])
                    if v_new is not None and (v_old is None or v_new > v_old):
                        task_map[task] = vals
        combined["tasks"] = [{t: task_map[t]} for t in sorted(task_map.keys())]
        merged.append(combined)
    return merged


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", default=None)
    parser.add_argument("--run_ids", nargs="*", default=None)
    parser.add_argument("--model_name", default=None)
    parser.add_argument("--model_url", default=None)
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--merge_per_model", action="store_true")
    args = parser.parse_args()

    api = wandb.Api()
    if args.run_ids:
        runs = [api.run(f"{PROJECT_PATH}/{rid}") for rid in args.run_ids]
    else:
        runs = api.runs(PROJECT_PATH)
        if args.tag:
            runs = [r for r in runs if args.tag in (r.tags or [])]

    records = []
    for r in runs:
        rec = run_to_record(
            r, override_name=args.model_name, override_url=args.model_url
        )
        if rec["tasks"]:
            records.append(rec)

    if args.merge_per_model:
        records = merge_by_model(records)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    print(f"✅ Wrote {len(records)} records to {args.out}")


if __name__ == "__main__":
    main()
