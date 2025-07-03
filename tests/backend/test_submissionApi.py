import io
import json
import zipfile

from fastapi.testclient import TestClient

from src.Backend.submission_api import app
import src.Backend.submission_api as submission_api

client = TestClient(app)


def make_zip(content: dict) -> io.BytesIO:

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w") as z:
        z.writestr("predictions.json", json.dumps(content))
    buf.seek(0)
    return buf


def test_health_check():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "healthy", "message": "API is running"}


def test_submit_missing_predictions_json():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w") as z:
        z.writestr("foo.txt", "bar")
    buf.seek(0)

    response = client.post(
        "/submit",
        data={"email": "alice@example.com", "display_name": "Alice"},
        files={"predictions_zip": ("test.zip", buf, "application/zip")},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Le ZIP ne contient pas predictions.json."
def test_submit_valid_predictions(monkeypatch, tmp_path):
    monkeypatch.setattr(submission_api, "RESULTS_DIR", tmp_path)
    class DummyPipeline:
        def __init__(self, *args, **kwargs):
            pass
        def evaluate(self):
            return
    monkeypatch.setattr(submission_api, 'Pipeline', DummyPipeline)

    valid_content = {"custom|qfrcola|0|0": [0]}
    valid_zip = make_zip(valid_content)
    response = client.post(
        "/submit",
        data={"email": "test@example.com", "display_name": "Tester"},
        files={"predictions_zip": ("valid.zip", valid_zip, "application/zip")},
    )
    assert response.status_code == 200
    data = response.json()
    assert "config_general" in data
    assert data["config_general"]["email"] == "test@example.com"
    assert data["config_general"]["display_name"] == "Tester"
    assert "predictions" in data
    assert "qfrcola" in data["predictions"]
    assert data["predictions"]["qfrcola"] == [0]

def test_submit_empty_predictions_dict():
    empty_zip = make_zip({})
    response = client.post(
        "/submit",
        data={"email": "bob@example.com", "display_name": "Bob"},
        files={"predictions_zip": ("empty.zip", empty_zip, "application/zip")},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Aucune tâche reconnue dans predictions.json."


def test_leaderboard_empty(monkeypatch, tmp_path):
    monkeypatch.setattr(submission_api, "RESULTS_DIR", tmp_path)

    response = client.get("/leaderboard")
    assert response.status_code == 200
    assert response.json() == []


def test_leaderboard_with_entries(monkeypatch, tmp_path):
    monkeypatch.setattr(submission_api, "RESULTS_DIR", tmp_path)

    sample1 = {
        "config_general": {
            "submission_id": "id1",
            "display_name": "User1",
            "zip_filename": "a.zip",
            "email": "u1@example.com",
        },
        "results": {"all": {"acc": 0.42}},
    }
    sample2 = {
        "config_general": {
            "submission_id": "id2",
            "display_name": "User2",
            "zip_filename": "b.zip",
            "email": "u2@example.com",
        },
        "results": {"all": {"acc": 0.99}},
    }
    p1 = tmp_path / "r1.json"
    p1.write_text(json.dumps(sample1))
    p2 = tmp_path / "r2.json"
    p2.write_text(json.dumps(sample2))

    response = client.get("/leaderboard")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list) and len(data) == 2
    assert data[0]["submission_id"] == "id1"
    assert data[0]["display_name"] == "User1"
    assert data[0]["score"] == 42.0
    assert data[1]["submission_id"] == "id2"
    assert data[1]["display_name"] == "User2"
    assert data[1]["score"] == 99.0


from uuid import UUID

from src.Backend.submission_api import (
    log_per_example_results,
    extract_aggregated_metrics,
    build_output_json,
)


class DummyTracker:
    def __init__(self, details: dict, results: dict):
        self.results = {"details": details, "results": results}


def test_log_per_example_results(capsys):
    details = {
        "custom|taskA|0|0": {"examples": [{"gold": "0", "pred": "1"}, {"gold": "1", "pred": "1"}]},
    }
    tracker = DummyTracker(details=details, results={})

    log_per_example_results(tracker)
    captured = capsys.readouterr().out
    assert "=== Per-example (gold vs pred) ===" in captured
    assert "--- Task taskA ---" in captured
    assert "gold='0'  pred='1'" in captured



def test_extract_aggregated_metrics(caplog):
    results = {
        "custom|taskX|0|0": {"acc": 0.8, "foo": "bar"},
        "taskY": {"precision": 0.5, "recall": 0.4, "note": None},
    }
    tracker = DummyTracker(details={}, results=results)

    metrics = extract_aggregated_metrics(tracker)
    assert metrics["taskX"] == {"acc": 0.8}
    assert metrics["taskY"] == {"precision": 0.5, "recall": 0.4}
    assert "=== Aggregated metrics ===" in caplog.text
    assert "taskX: {'acc': 0.8}" in caplog.text
    assert "taskY: {'precision': 0.5, 'recall': 0.4}" in caplog.text


def test_build_output_json_structure_and_content():
    email = "alice@example.com"
    display_name = "Alice"
    zip_filename = "preds.zip"
    results = {"task1": {"acc": 0.33}, "all": {"acc": 0.33}}
    tasks_dict = {"task1": [0, 1, 1], "task2": [1, 0, 0]}
    available_tasks = ["task1"]
    max_samples = 2

    out = build_output_json(
        email=email,
        display_name=display_name,
        predictions_zip_filename=zip_filename,
        results=results,
        tasks_prediction_dictionary=tasks_dict,
        available_tasks=available_tasks,
        max_samples=max_samples
    )
    assert "config_general" in out and "results" in out and "predictions" in out
    cfg = out["config_general"]
    assert cfg["email"] == email
    assert cfg["display_name"] == display_name
    assert cfg["zip_filename"] == zip_filename
    UUID(cfg["submission_id"])
    assert out["results"] == results
    assert set(out["predictions"].keys()) == {"task1"}
    assert out["predictions"]["task1"] == [0, 1]
