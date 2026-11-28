#!/usr/bin/env python3
"""Merge ``<model>_metrics.json`` files of the evaluation pipelines into the leaderboard.

Usage:
    scripts/aggregate_results.py DIR [DIR ...] [--models NAME ...] [--replace-tasks T ...]
        [--min-tasks 24] [--leaderboard cole/backend/results/leaderboard.json] [--dry-run]

Rules:
  * A task entry is kept only if it was computed on the whole test set. Entries whose
    ``*_warning`` says the prediction size differs from the ground-truth size (smoke tests
    with ``--max_examples``, partial runs) are ignored. When a task appears several times,
    the last complete entry wins.
  * Values are stored in percent, like the existing leaderboard: accuracy and wsd exact
    match are fractions in the metrics files (x100); fquad and piaf are already in percent.
  * A model absent from the leaderboard is added if it has at least ``--min-tasks`` tasks.
  * A model already present is never modified, except for the tasks of ``--replace-tasks``.
"""

import argparse
import json
import re
from pathlib import Path

SIZE_WARNING = re.compile(
    r"prediction size is of '(\d+)', while the ground truths size is of '(\d+)'"
)
PERCENT_ALREADY = {"fquad", "piaf"}  # tasks whose metrics are already in percent


def _warnings(payload):
    found = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            if isinstance(value, str) and key.endswith("_warning"):
                match = SIZE_WARNING.search(value)
                if match:
                    found.append((int(match.group(1)), int(match.group(2))))
            else:
                found.extend(_warnings(value))
    return found


def _metrics(task, payload):
    """Flatten ``{group: {metric: value, metric_warning: ...}}`` into percent values."""
    out = {}
    for group in payload.values():
        if not isinstance(group, dict):
            continue
        for metric, value in group.items():
            if metric.endswith("_warning") or not isinstance(value, (int, float)):
                continue
            out[metric] = value if task in PERCENT_ALREADY else value * 100
    return out


def load_model(path):
    """Return (model_name, {task: metrics}) keeping complete task entries only."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    tasks = {}
    for entry in data.get("tasks", []):
        task, payload = next(iter(entry.items()))
        if any(pred != truth for pred, truth in _warnings(payload)):
            continue
        metrics = _metrics(task, payload)
        if metrics:
            tasks[task] = metrics
    return data["model_name"], tasks


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("dirs", nargs="+")
    parser.add_argument("--models", nargs="*", default=None)
    parser.add_argument("--replace-tasks", nargs="*", default=[])
    parser.add_argument("--min-tasks", type=int, default=24)
    parser.add_argument(
        "--leaderboard", default="cole/backend/results/leaderboard.json"
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    board_path = Path(args.leaderboard)
    original = board_path.read_text(encoding="utf-8")
    board = json.loads(original)
    by_name = {entry["model_name"]: entry for entry in board}

    collected = {}
    for directory in args.dirs:
        for path in sorted(Path(directory).expanduser().glob("*_metrics.json")):
            name, tasks = load_model(path)
            if args.models and name not in args.models:
                continue
            collected.setdefault(name, {}).update(tasks)

    for name, tasks in sorted(collected.items()):
        if name in by_name:
            if not args.replace_tasks:
                print(f"= {name}: already on the leaderboard, left untouched")
                continue
            wanted = {t: tasks[t] for t in args.replace_tasks if t in tasks}
            missing = [t for t in args.replace_tasks if t not in tasks]
            if missing:
                print(f"! {name}: no complete result for {missing}")
            entry = by_name[name]
            entry["tasks"] = [
                {t: wanted[t]} if t in wanted else item
                for item in entry["tasks"]
                for t in [next(iter(item))]
            ]
            have = {next(iter(item)) for item in entry["tasks"]}
            entry["tasks"] += [{t: m} for t, m in wanted.items() if t not in have]
            print(f"~ {name}: replaced {sorted(wanted)}")
        elif len(tasks) >= args.min_tasks:
            entry = {"model_name": name, "tasks": [{t: m} for t, m in tasks.items()]}
            if "/" in name:
                entry["model_url"] = f"https://huggingface.co/{name}"
            board.append(entry)
            print(f"+ {name}: added with {len(tasks)} tasks")
        else:
            print(f"- {name}: only {len(tasks)} complete tasks, skipped")

    if not args.dry_run:
        text = json.dumps(board, ensure_ascii=False, indent=2)
        if original.endswith("\n"):
            text += "\n"
        board_path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
