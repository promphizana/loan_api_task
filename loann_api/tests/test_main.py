import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("GIT_SHA", raising=False)
    monkeypatch.setenv("MODEL_PATH", "model/model.json")
    with TestClient(main.app) as c:
        yield c


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert r.json()["git_sha"] == "unknown"


def test_health_includes_git_sha(client, monkeypatch):
    monkeypatch.setenv("GIT_SHA", "abc123")
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["git_sha"] == "abc123"


def test_predict(client):
    r = client.post("/predict", json={"amount_usd": 1500, "term_months": 12,
                                      "monthly_income_usd": 400})
    assert r.status_code == 200
    body = r.json()
    assert body["default_probability"] == pytest.approx(0.2975, abs=1e-3)
    assert body["risk_band"] == "medium"


def test_risk_bands(client):
    low = client.post("/predict", json={"amount_usd": 500, "term_months": 6,
                                        "monthly_income_usd": 600}).json()
    high = client.post("/predict", json={"amount_usd": 5000, "term_months": 24,
                                         "monthly_income_usd": 100}).json()
    assert low["risk_band"] == "low"
    assert high["risk_band"] == "high"


@pytest.mark.parametrize("payload", [
    {},
    {"amount_usd": 50, "term_months": 12, "monthly_income_usd": 400},
    {"amount_usd": 1500, "term_months": 10, "monthly_income_usd": 400},
    {"amount_usd": 1500, "term_months": 12, "monthly_income_usd": 0},
])
def test_predict_invalid(client, payload):
    assert client.post("/predict", json=payload).status_code == 422


def test_model_path_is_configurable(monkeypatch, tmp_path):
    monkeypatch.setenv("MODEL_PATH", str(tmp_path / "missing.json"))
    with pytest.raises(FileNotFoundError):
        with TestClient(main.app):
            pass
