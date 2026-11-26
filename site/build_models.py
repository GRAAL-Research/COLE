"""Precompute data/models.json from data/leaderboard-snapshot.json.

Score rules copied from the live site (frontend/src/app/leaderboard/util.js and
getCellValue in leaderboard/page.js): a task score is the mean of its allowed
metrics; values above 1 are divided by 100. Missing tasks are never zero-filled:
a category score is the mean of the tasks the model has, with the task count kept.
Submitter emails are never copied.

Run from the repo root: python3 site/build_models.py (normally through site/refresh_data.py).
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
# Decision pending the re-run: keep the leaderboard values as published. Switch to True to turn the
# unreliable free-text scores (fquad, piaf, wsd of 10 API entries) into n.d. (see unreliable_tasks).
APPLY_UNRELIABLE_TASKS = False
PRED = REPO_ROOT / "predictions"
ALLOWED = {
    "acc",
    "accuracy",
    "f1",
    "exact_match",
    "fquad",
    "pearson",
    "pearsonr",
    "spearman",
}
SNAPSHOT_DATE = "2026-11-26"
SIZES_FILE = PRED / "models_size.json"
# Sizes read by hand from predictions/llm_details.csv (billions of parameters) for entries whose id is
# not a key of models_size.json. See data/inputs/README.md for the provenance.
SIZE_FROM_DETAILS_FILE = ROOT / "data/inputs/size_from_details.json"

CLOSED = re.compile(
    r"^(gpt-(?!oss)|o1|o3|claude|grok|google/gemini|pixtral|mistral-large|deepseek-(chat|reasoner)|qwen/qwen-max)"
)


def normalize(name: str) -> str:
    parts = name.lower().split("|")
    return parts[1].replace("-", "_") if len(parts) >= 2 else name.lower()


def raw_metrics(entry: dict, task: str) -> dict:
    """Raw metric values of one task (before the /100 rule), merged over its metric groups."""
    out = {}
    for raw, groups in entry["results"].items():
        if normalize(raw) == task:
            for group in groups.values():
                if isinstance(group, dict):
                    out.update(
                        {
                            m.lower(): v
                            for m, v in group.items()
                            if isinstance(v, (int, float))
                        }
                    )
    return out


def unreliable_tasks(entry: dict, kind: str) -> set:
    """Decision of 2026-11-26: for an API entry whose fquad is exactly 0 on f1 and exact_match, the free-text
    scores are very probably an evaluation failure (raw predictions unavailable). Those tasks become n.d.:
    fquad (f1 == 0 and exact_match == 0), piaf (same rule), wsd (raw exact_match below 2, i.e. the exact zeros
    plus the two near-zero entries named in the audit: 0.16 and 1.2). Only the entries hit by the fquad rule
    are touched; the random baseline keeps its zeros (not an API entry)."""
    if not APPLY_UNRELIABLE_TASKS or kind != "api":
        return set()
    fq = raw_metrics(entry, "fquad")
    if not (fq.get("f1") == 0 and fq.get("exact_match") == 0):
        return set()
    out = {"fquad"}
    pi = raw_metrics(entry, "piaf")
    if pi.get("f1") == 0 and pi.get("exact_match") == 0:
        out.add("piaf")
    ws = raw_metrics(entry, "wsd")
    if ws.get("exact_match") is not None and ws["exact_match"] < 2:
        out.add("wsd")
    return out


def task_scores(entry: dict, skip=frozenset()) -> dict:
    out = {}
    for raw, groups in entry["results"].items():
        if normalize(raw) in skip:
            continue
        values = []
        for group in groups.values():
            if isinstance(group, dict):
                for metric, value in group.items():
                    if (
                        "_warning" not in metric
                        and isinstance(value, (int, float))
                        and metric.lower() in ALLOWED
                    ):
                        values.append(value)
        if values:
            norm = [v / 100 if v > 1 else v for v in values]
            out[normalize(raw)] = sum(norm) / len(norm)
    return out


def site_overall(entry: dict, skip=frozenset()):
    """computeAverageScore from util.js: mean over metric groups (n.d. tasks are left out, never zero)."""
    per = []
    for raw, groups in entry["results"].items():
        if normalize(raw) in skip:
            continue
        for group in groups.values():
            if isinstance(group, dict):
                vals = [
                    v
                    for m, v in group.items()
                    if m.lower() in ALLOWED and isinstance(v, (int, float))
                ]
                if vals:
                    norm = [v / 100 if v > 1 else v for v in vals]
                    per.append(sum(norm) / len(norm))
    return sum(per) / len(per) if per else None


def pretty(name: str) -> str:
    base = name.split("/")[-1]
    base = re.sub(r"-?(unsloth-)?bnb-4bit$", "", base)
    base = re.sub(r"-unsloth$", "", base)
    base = re.sub(r"-(\d{4}-\d{2}-\d{2}|\d{8}|\d{4})$", "", base)
    return base


def label(name: str) -> str:
    """Readable name for lists: Claude Opus 4, GPT-4o, Qwen3 14B."""
    if name == "RandomBaselineModel":
        return "Random guessing"
    parts = pretty(name).split("-")
    if parts[0] == "gpt" and len(parts) > 1:
        return (
            "GPT-" + parts[1] + ("" if len(parts) == 2 else " " + " ".join(parts[2:]))
        )
    if parts[0] == "claude":
        return " ".join(p.capitalize() if not p[0].isdigit() else p for p in parts)
    text = " ".join(parts)
    if re.match(r"^o\d", text):
        return text
    text = text.replace("deepseek", "DeepSeek")
    return text[0].upper() + text[1:]


FAMILIES = [
    (r"Chocolatine|French-Alpaca", "French community fine-tunes"),
    (r"Deepthink", "prithivMLmods"),
    (r"claude", "Anthropic"),
    (r"^(gpt|o1|o3|chatgpt)|gpt-oss", "OpenAI"),
    (r"gemini|gemma", "Google"),
    (r"grok", "xAI"),
    (r"mistral|pixtral|mixtral", "Mistral AI"),
    (r"deepseek", "DeepSeek"),
    (r"llama", "Meta"),
    (r"qwen|Qwen|QwQ", "Alibaba (Qwen)"),
    (r"phi", "Microsoft"),
    (r"OLMo", "AI2"),
    (r"granite", "IBM"),
    (r"SmolLM", "Hugging Face"),
    (r"aya", "Cohere"),
    (r"Lucie|Croissant", "OpenLLM-France"),
    (r"Apertus", "Swiss AI"),
    (r"reka", "Reka"),
    (r"s1\.1", "Simplescaling"),
    (r"Random", "Reference"),
]


def family(name: str) -> str:
    base = name.split("/")[-1]
    for pat, fam in FAMILIES:
        if re.search(pat, base, re.IGNORECASE):
            return fam
    return "unknown"


def dated(name: str):
    """Month (YYYY-MM) only when the id carries a full date (YYYYMMDD or YYYY-MM-DD); otherwise None."""
    m = re.search(r"-(20\d{2})-?(\d{2})-?(\d{2})$", name)
    return f"{m.group(1)}-{m.group(2)}" if m else None


def category_scores(tasks: dict, categories: list) -> dict:
    """Mean of the tasks a model has in each category, with the count kept (missing tasks are never zero)."""
    cats = {}
    for cat in categories:
        have = [tasks[t] for t in cat["tasks"] if t in tasks]
        cats[cat["key"]] = {
            "score": round(sum(have) / len(have), 6) if have else None,
            "n": len(have),
            "of": len(cat["tasks"]),
        }
    return cats


def model_size(name: str, sizes: dict, size_from_details: dict):
    """Size in billions of parameters and where it comes from, or (None, None)."""
    if name in sizes:
        return round(sizes[name] / 1e9, 2), "models_size.json"
    if name in size_from_details:
        return size_from_details[name], "llm_details.csv"
    return None, None


def build_model(
    entry: dict, categories: list, sizes: dict, size_from_details: dict
) -> dict:
    """One row of models.json from one leaderboard entry."""
    name = entry["display_name"]
    kind = "api" if CLOSED.match(name) else "open"
    na = unreliable_tasks(entry, kind)
    tasks = task_scores(entry, na)
    tasks.pop("frblimp", None)  # duplicate of qfrblimp, see categories.json
    size_b, size_src = model_size(name, sizes, size_from_details)
    overall = site_overall(entry, na)
    return {
        "id": name,
        "name": pretty(name),
        "label": label(name),
        "kind": kind,
        "quantized_4bit": "bnb-4bit" in name,
        "family": family(name),
        "date": dated(name),
        "size_b": size_b,
        "size_source": size_src,
        "protocol": "paper-v1",
        "snapshot": SNAPSHOT_DATE,
        "overall": None if overall is None else round(overall, 6),
        "tasks_done": len(tasks),
        "unreliable_tasks": sorted(na),
        "categories": category_scores(tasks, categories),
        "tasks": {k: round(v, 6) for k, v in sorted(tasks.items())},
    }


def rank_models(models: list) -> list:
    """Sort by overall score (best first) and set a competition rank: equal scores share a rank."""
    models.sort(key=lambda m: -m["overall"])
    rank = 0
    prev = None
    for i, m in enumerate(models):
        if m["overall"] != prev:
            rank = i + 1
        m["rank"] = rank
        prev = m["overall"]
    return models


def build_all(
    snapshot: list, categories: list, sizes: dict, size_from_details: dict
) -> list:
    models = [
        build_model(entry, categories, sizes, size_from_details) for entry in snapshot
    ]
    assert len({m["label"] for m in models}) == len(models), "label collision"
    return rank_models(models)


def require(path: Path) -> Path:
    if not path.exists():
        sys.exit(
            f"build_models: missing input {path} (see site/README.md, section Data refresh)"
        )
    return path


def main() -> None:
    snapshot = json.loads(require(ROOT / "data/leaderboard-snapshot.json").read_text())
    categories = json.loads(require(ROOT / "data/categories.json").read_text())[
        "categories"
    ]
    sizes = json.loads(require(SIZES_FILE).read_text())
    size_from_details = json.loads(require(SIZE_FROM_DETAILS_FILE).read_text())
    models = build_all(snapshot, categories, sizes, size_from_details)
    out = {"snapshot": SNAPSHOT_DATE, "protocol": "paper-v1", "models": models}
    (ROOT / "data/models.json").write_text(
        json.dumps(out, ensure_ascii=False, separators=(",", ":"))
    )
    for m in models:
        c = m["categories"]
        scores = " ".join(f'{(c[k]["score"] or 0) * 100:5.1f}' for k in c)
        print(
            f'{m["rank"]:>3} {m["name"][:38]:38} {m["kind"]:6} {str(m["size_b"]):>6} {m["overall"] * 100:5.1f} {scores} n={m["tasks_done"]}'
        )
    hits = [(m["id"], m["unreliable_tasks"]) for m in models if m["unreliable_tasks"]]
    print("N.D. HITS", len(hits), sum(len(h[1]) for h in hits))
    for h in hits:
        print("  ", h[0], h[1])


if __name__ == "__main__":
    main()
