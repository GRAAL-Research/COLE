import io
import json
import uuid
import zipfile

from fastapi.testclient import TestClient

from src.backend import submission_api
from src.backend.submission_api import (
    app,
)

client = TestClient(app)


def make_zip(content: dict) -> io.BytesIO:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w") as z:
        z.writestr("predictions.json", json.dumps(content))
    buf.seek(0)
    return buf


def make_wrong_zip(content: dict) -> io.BytesIO:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w") as z:
        z.writestr("wrong.json", json.dumps(content))
    buf.seek(0)
    return buf


def test_health_check():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "healthy", "message": "API is running."}


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
    assert (
        response.json()["detail"]
        == "The uploaded ZIP file does not contains a predictions.json file."
    )


def test_submit_valid_predictions(monkeypatch, tmp_path):
    monkeypatch.setattr(submission_api, "RESULTS_DIR", tmp_path)

    valid_content = {
        "model_name": "a_model_name",
        "model_url": "a_model_url",
        "tasks": [
            {"allocine": {"predictions": [1, 1, 1, 1, 1]}},
            {
                "fquad": {
                    "predictions": [
                        "par un mauvais état de santé",
                        "par un mauvais état de santé",
                        "par un mauvais état de santé",
                        "par un mauvais état de santé",
                        "par un mauvais état de santé",
                    ]
                }
            },
        ],
    }
    valid_zip = make_zip(valid_content)
    response = client.post(
        "/submit",
        data={"email": "test@example.com", "display_name": "Tester"},
        files={"predictions_zip": ("valid.zip", valid_zip, "application/zip")},
    )
    assert response.status_code == 200
    data = response.json()

    assert data.get("display_name") == "Tester"
    assert data.get("tasks")[0].get("allocine").get("accuracy") is not None


def test_submit_wrong_file_name_predictions_dict():
    wrong_zip = make_wrong_zip({})
    response = client.post(
        "/submit",
        data={"email": "bob@example.com", "display_name": "Bob"},
        files={"predictions_zip": ("empty.zip", wrong_zip, "application/zip")},
    )
    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "The uploaded ZIP file does not contains a predictions.json file."
    )


def test_leaderboard_empty(monkeypatch, tmp_path):
    monkeypatch.setattr(submission_api, "RESULTS_DIR", tmp_path)

    response = client.get("/leaderboard")
    assert response.status_code == 200
    assert response.json() == []


def test_leaderboard_with_entries(monkeypatch, tmp_path):
    monkeypatch.setattr(submission_api, "RESULTS_DIR", tmp_path)

    sample1 = {
        "display_name": "User1",
        "model_name": "a_model_name",
        "model_url": "a_model_url",
        "tasks": [
            {
                "allocine": {
                    "accuracy": {
                        "accuracy": 0.4,
                        "accuracy_warning": "Your prediction size is of '5', while the "
                        "ground truths size is of '20000'."
                        " We computed the metric over the first 5 elements.",
                    },
                }
            },
            {
                "fquad": {
                    "fquad": {
                        "exact_match": 20.0,
                        "f1": 25.33333333332,
                        "fquad_warning": "Your prediction size is of '5', "
                        "while the ground truths size is of '400'. "
                        "We computed the metric over the first 5 elements.",
                    },
                }
            },
        ],
    }
    sample2 = {
        "display_name": "User2",
        "model_name": "a_model_name_2",
        "model_url": "a_model_url_2",
        "tasks": [
            {
                "allocine": {
                    "accuracy": {
                        "accuracy": 0.4,
                        "accuracy_warning": "Your prediction size is of '5', while the "
                        "ground truths size is of '20000'."
                        " We computed the metric over the first 5 elements.",
                    },
                }
            },
            {
                "fquad": {
                    "fquad": {
                        "exact_match": 20.0,
                        "f1": 25.33333333332,
                        "fquad_warning": "Your prediction size is of '5', "
                        "while the ground truths size is of '400'. "
                        "We computed the metric over the first 5 elements.",
                    },
                }
            },
        ],
    }
    uuid_1 = uuid.uuid4()
    p1 = tmp_path / f"{uuid_1}.json"
    p1.write_text(json.dumps(sample1))
    uuid_2 = uuid.uuid4()
    p2 = tmp_path / f"{uuid_2}.json"
    p2.write_text(json.dumps(sample2))

    response = client.get("/leaderboard")
    assert response.status_code == 200
    data = response.json()
    # TODO
    print(data)
