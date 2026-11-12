import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key")
    monkeypatch.setenv("MODEL_PATH", "model/model.json")
    with TestClient(main.app) as c:
        yield c


def test_predict_without_api_key_returns_401(client):
    response = client.post(
        "/predict",
        json={"amount_usd": 1500, "term_months": 12, "monthly_income_usd": 400},
    )
    assert response.status_code == 401


def test_predict_with_wrong_api_key_returns_401(client):
    response = client.post(
        "/predict",
        json={"amount_usd": 1500, "term_months": 12, "monthly_income_usd": 400},
        headers={"X-API-Key": "wrong-key"},
    )
    assert response.status_code in (401, 403)


def test_predict_with_valid_api_key_returns_200(client):
    response = client.post(
        "/predict",
        json={"amount_usd": 1500, "term_months": 12, "monthly_income_usd": 400},
        headers={"X-API-Key": "test-key"},
    )
    assert response.status_code == 200


def test_predict_fails_closed_when_api_key_is_unset(client, monkeypatch):
    monkeypatch.delenv("API_KEY", raising=False)
    payload = {
        "amount_usd": 1500,
        "term_months": 12,
        "monthly_income_usd": 400,
    }
    headers = {"X-API-Key": "test-key"}
    response = client.post(
        "/predict",
        json=payload,
        headers=headers,
    )
    assert response.status_code == 503

    monkeypatch.setenv("API_KEY", "")
    response = client.post("/predict", json=payload, headers=headers)
    assert response.status_code == 503


def test_health_is_public_without_api_key(client, monkeypatch):
    monkeypatch.delenv("API_KEY", raising=False)
    response = client.get("/health")
    assert response.status_code == 200
