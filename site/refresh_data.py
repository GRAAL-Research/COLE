"""Regenerate the site data from the repository's own files.

Run from the repo root: python3 site/refresh_data.py [--keep-snapshot-models]

Pipeline:
  1. cole/backend/results/leaderboard.json  ->  site/data/leaderboard-snapshot.json
     (reshaped to the live API format that build_models.py reads; emails are never copied)
  2. site/build_models.py   ->  site/data/models.json
     (inputs: the snapshot, data/categories.json, predictions/models_size.json,
      data/inputs/size_from_details.json)
  3. site/build_extra.py    ->  site/data/extra.json
     (chance references computed from models.json; quiz items are hand-written in the script)

Pages are not rebuilt here: run python3 site/build_pages.py afterwards.

--keep-snapshot-models keeps only the models already present in the committed snapshot, which
restricts the run to those models. Without it, every entry of leaderboard.json is used.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
LEADERBOARD = REPO_ROOT / "cole/backend/results/leaderboard.json"
SNAPSHOT = ROOT / "data/leaderboard-snapshot.json"
REQUIRED_INPUTS = [
    LEADERBOARD,
    ROOT / "data/categories.json",
    REPO_ROOT / "predictions/models_size.json",
    REPO_ROOT / "predictions/all_llms.py",
    ROOT / "data/inputs/size_from_details.json",
]
# The live API names the metric group "fquad" for the free-text tasks and "accuracy" for all others.
FREE_TEXT_TASKS = {"fquad", "piaf", "wsd"}


def check_inputs() -> None:
    missing = [p for p in REQUIRED_INPUTS if not p.exists()]
    if missing:
        lines = "\n".join(f"  - {p}" for p in missing)
        sys.exit(f"refresh_data: missing input file(s), nothing was changed:\n{lines}")


def entry_to_snapshot(entry: dict, submission_id: str) -> dict:
    """Reshape a repo leaderboard entry ({model_name, tasks: [{task: {metric: v}}]}) to the API shape."""
    results = {}
    for task_dict in entry["tasks"]:
        for task, metrics in task_dict.items():
            group = "fquad" if task in FREE_TEXT_TASKS else "accuracy"
            results[task] = {group: dict(metrics)}
    return {
        "submission_id": submission_id,
        "display_name": entry["model_name"],
        "email": "N/A",
        "results": results,
    }


def build_snapshot(
    leaderboard: list, previous: list, keep_snapshot_models: bool
) -> list:
    """Snapshot entries from the repo leaderboard; submission ids are kept from the previous snapshot."""
    ids = {e["display_name"]: e["submission_id"] for e in previous}
    if keep_snapshot_models:
        leaderboard = [e for e in leaderboard if e["model_name"] in ids]
    return [
        entry_to_snapshot(e, ids.get(e["model_name"], f"repo:{e['model_name']}"))
        for e in leaderboard
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", maxsplit=1)[0])
    parser.add_argument("--keep-snapshot-models", action="store_true")
    args = parser.parse_args()
    check_inputs()
    leaderboard = json.loads(LEADERBOARD.read_text())
    previous = json.loads(SNAPSHOT.read_text()) if SNAPSHOT.exists() else []
    snapshot = build_snapshot(leaderboard, previous, args.keep_snapshot_models)
    SNAPSHOT.write_text(json.dumps(snapshot, ensure_ascii=False))
    print(
        f"snapshot: {len(snapshot)} entries from {LEADERBOARD.relative_to(REPO_ROOT)}"
    )
    for script in ("build_models.py", "build_extra.py"):
        subprocess.run([sys.executable, str(ROOT / script)], check=True, cwd=REPO_ROOT)


if __name__ == "__main__":
    main()
