"""Pure data logic of the static site build (site/build_models.py and site/refresh_data.py).

No network, no dataset access: entries are built in memory.
"""

import importlib.util
import json
from pathlib import Path

import pytest

SITE_DIR = Path(__file__).resolve().parents[2] / "site"


def load_module(name: str):
    spec = importlib.util.spec_from_file_location(
        f"site_{name}", SITE_DIR / f"{name}.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


build_models = load_module("build_models")
refresh_data = load_module("refresh_data")

CATEGORIES = [
    {"key": "grammar", "tasks": ["multiblimp", "qfrblimp", "qfrcola"]},
    {"key": "reading", "tasks": ["fquad", "piaf"]},
]


def make_entry(name: str, **tasks) -> dict:
    """Entry in the live API shape: results[task][group][metric]."""
    results = {}
    for task, metrics in tasks.items():
        group = "fquad" if task in {"fquad", "piaf", "wsd"} else "accuracy"
        results[task] = {group: metrics}
    return {
        "submission_id": "x",
        "display_name": name,
        "email": "N/A",
        "results": results,
    }


def test_task_score_normalizes_percent_and_averages_metrics():
    entry = make_entry("m", fquad={"f1": 60.0, "exact_match": 0.4})
    # 60 -> 0.6 (value above 1 divided by 100), 0.4 kept; mean = 0.5
    assert build_models.task_scores(entry)["fquad"] == pytest.approx(0.5)


def test_task_score_ignores_warning_and_unknown_metrics():
    entry = make_entry(
        "m", qfrcola={"accuracy": 80.0, "accuracy_warning": 5, "bleu": 3}
    )
    assert build_models.task_scores(entry)["qfrcola"] == pytest.approx(0.8)


def test_category_means_use_only_present_tasks_and_keep_counts():
    tasks = {"multiblimp": 0.9, "qfrcola": 0.5}
    cats = build_models.category_scores(tasks, CATEGORIES)
    assert cats["grammar"] == {"score": pytest.approx(0.7), "n": 2, "of": 3}
    # No task of the category: score is None (n.d.), never zero.
    assert cats["reading"] == {"score": None, "n": 0, "of": 2}


def test_frblimp_duplicate_is_dropped_from_tasks():
    entry = make_entry("m", frblimp={"accuracy": 50.0}, qfrblimp={"accuracy": 50.0})
    row = build_models.build_model(entry, CATEGORIES, {}, {})
    assert "frblimp" not in row["tasks"]
    assert row["tasks_done"] == 1


def test_ranking_orders_by_overall_and_ties_share_a_rank():
    models = [
        {"id": "low", "overall": 0.2},
        {"id": "top", "overall": 0.9},
        {"id": "tie_a", "overall": 0.5},
        {"id": "tie_b", "overall": 0.5},
    ]
    ranked = build_models.rank_models(models)
    assert [m["id"] for m in ranked][0] == "top"
    assert [m["rank"] for m in ranked] == [1, 2, 2, 4]
    assert ranked[-1]["id"] == "low"


def test_size_prefers_models_size_then_details_then_none():
    sizes = {"a": 8_030_000_000}
    details = {"b": 46.7}
    assert build_models.model_size("a", sizes, details) == (8.03, "models_size.json")
    assert build_models.model_size("b", sizes, details) == (46.7, "llm_details.csv")
    assert build_models.model_size("c", sizes, details) == (None, None)


def zero_free_text_entry(name: str) -> dict:
    return make_entry(
        name,
        fquad={"f1": 0.0, "exact_match": 0.0},
        piaf={"f1": 0.0, "exact_match": 0.0},
        wsd={"exact_match": 0.0},
        qfrcola={"accuracy": 80.0},
    )


def test_unreliable_zeros_kept_when_flag_is_off(monkeypatch):
    monkeypatch.setattr(build_models, "APPLY_UNRELIABLE_TASKS", False)
    row = build_models.build_model(zero_free_text_entry("gpt-4o"), CATEGORIES, {}, {})
    assert row["unreliable_tasks"] == []
    assert row["tasks"]["fquad"] == 0.0
    assert row["tasks_done"] == 4


def test_unreliable_tasks_become_nd_when_flag_is_on(monkeypatch):
    monkeypatch.setattr(build_models, "APPLY_UNRELIABLE_TASKS", True)
    row = build_models.build_model(zero_free_text_entry("gpt-4o"), CATEGORIES, {}, {})
    assert row["kind"] == "api"
    assert row["unreliable_tasks"] == ["fquad", "piaf", "wsd"]
    # n.d. means absent, not zero: the tasks vanish and the overall mean ignores them.
    assert set(row["tasks"]) == {"qfrcola"}
    assert row["overall"] == pytest.approx(0.8)
    assert row["categories"]["reading"]["score"] is None
    assert row["categories"]["reading"]["n"] == 0


def test_flag_leaves_open_models_untouched(monkeypatch):
    monkeypatch.setattr(build_models, "APPLY_UNRELIABLE_TASKS", True)
    row = build_models.build_model(
        zero_free_text_entry("Qwen/Qwen3-14B"), CATEGORIES, {}, {}
    )
    assert row["kind"] == "open"
    assert row["unreliable_tasks"] == []
    assert row["tasks"]["fquad"] == 0.0


def test_flag_needs_fquad_to_be_exactly_zero(monkeypatch):
    monkeypatch.setattr(build_models, "APPLY_UNRELIABLE_TASKS", True)
    entry = make_entry(
        "gpt-4o",
        fquad={"f1": 30.0, "exact_match": 0.0},
        wsd={"exact_match": 0.0},
    )
    assert build_models.unreliable_tasks(entry, "api") == set()


def test_label_collision_is_rejected():
    entries = [
        make_entry("org-a/Same-Model", qfrcola={"accuracy": 50.0}),
        make_entry("org-b/Same-Model", qfrcola={"accuracy": 60.0}),
    ]
    with pytest.raises(AssertionError, match="label collision"):
        build_models.build_all(entries, CATEGORIES, {}, {})


def test_refresh_reshapes_repo_entry_to_api_shape():
    repo_entry = {
        "model_name": "m",
        "model_url": "https://example.org",
        "tasks": [
            {"allocine": {"accuracy": 47.0}},
            {"fquad": {"f1": 1.0, "exact_match": 0.0}},
        ],
    }
    out = refresh_data.entry_to_snapshot(repo_entry, "sid")
    assert out["email"] == "N/A"
    assert out["results"]["allocine"] == {"accuracy": {"accuracy": 47.0}}
    assert out["results"]["fquad"] == {"fquad": {"f1": 1.0, "exact_match": 0.0}}


def test_refresh_keep_snapshot_models_filters_and_keeps_ids():
    leaderboard = [
        {"model_name": "old", "tasks": [{"allocine": {"accuracy": 1.0}}]},
        {"model_name": "new", "tasks": [{"allocine": {"accuracy": 2.0}}]},
    ]
    previous = [{"display_name": "old", "submission_id": "abc"}]
    kept = refresh_data.build_snapshot(leaderboard, previous, True)
    assert [e["display_name"] for e in kept] == ["old"]
    assert kept[0]["submission_id"] == "abc"
    everything = refresh_data.build_snapshot(leaderboard, previous, False)
    assert [e["display_name"] for e in everything] == ["old", "new"]
    assert everything[1]["submission_id"] == "repo:new"


def test_committed_models_json_matches_committed_snapshot():
    """The committed models.json must be what the pipeline produces from the committed inputs."""
    snapshot = json.loads((SITE_DIR / "data/leaderboard-snapshot.json").read_text())
    categories = json.loads((SITE_DIR / "data/categories.json").read_text())[
        "categories"
    ]
    sizes = json.loads(build_models.SIZES_FILE.read_text())
    details = json.loads(build_models.SIZE_FROM_DETAILS_FILE.read_text())
    expected = build_models.build_all(snapshot, categories, sizes, details)
    committed = json.loads((SITE_DIR / "data/models.json").read_text())["models"]
    assert committed == expected


def test_family_cohere_command_models():
    assert build_models.family("command-r7b-12-2024") == "Cohere"
    assert build_models.family("CohereForAI/aya-expanse-32b") == "Cohere"


def test_published_pages_follow_the_data():
    """Counts shown on the pages come from models.json: no stale hardcoded count."""
    data = json.loads((SITE_DIR / "data/models.json").read_text())
    n = len(data["models"])
    index = (SITE_DIR / "index.html").read_text()
    assert f"{n} models" in index
    for page in ("index.html", "all-results.html", "model.html"):
        html = (SITE_DIR / page).read_text()
        assert "{N_" not in html and "{Q_" not in html
        if n != 96:
            assert "96 models" not in html and "96 modèles" not in html
