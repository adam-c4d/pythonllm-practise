from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from main import app

SMALL = {"carat": 0.5, "cut": "Ideal", "color": "E", "clarity": "VS1",
         "depth": 61.5, "table": 56.0}
BIG = {"carat": 2.0, "cut": "Good", "color": "J", "clarity": "I1",
       "depth": 63.0, "table": 59.0}


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:  # `with` runs the lifespan: loads the model
        yield test_client


def test_health(client):
    response = client.get("/health")
    assert response.json() == {"status": "ok", "model_loaded": True}


def test_predict_one(client):
    response = client.post("/predict", json=SMALL)
    assert response.status_code == 200
    assert response.json() == {"price": 1773}


def test_batch_matches_single(client):
    response = client.post("/predict/batch", json=[SMALL, BIG])
    assert response.json() == {"count": 2, "prices": [1773, 6713]}


def test_unknown_cut_is_422(client):
    response = client.post("/predict", json=SMALL | {"cut": "Excellent"})
    assert response.status_code == 422
    error = response.json()["detail"][0]
    assert error["loc"] == ["body", "cut"]
    assert error["type"] == "literal_error"


def test_summary_of_small_csv(client):
    csv_text = "carat,cut,price\n0.5,Ideal,1800\n1.0,,4600\n"
    files = {"file": ("small.csv", csv_text, "text/csv")}
    response = client.post("/summary", files=files)
    assert response.status_code == 200
    body = response.json()
    assert body["rows"] == 2
    assert body["missing_values"] == {"cut": 1}
    assert body["numeric_means"] == {"carat": 0.75, "price": 3200.0}


def test_summary_rejects_other_files(client):
    files = {"file": ("notes.txt", "hello", "text/plain")}
    response = client.post("/summary", files=files)
    assert response.status_code == 400


def test_missing_model_gives_503(monkeypatch):
    monkeypatch.setenv("MODEL_PATH", "no_such_file.joblib")
    with TestClient(app) as client:
        assert client.get("/health").json()["model_loaded"] is False
        assert client.post("/predict", json=SMALL).status_code == 503
