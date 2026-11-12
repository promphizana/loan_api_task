from fastapi.testclient import TestClient

import main


def test_health_reports_git_sha(monkeypatch):
    monkeypatch.setenv("GIT_SHA", "abc1234")
    with TestClient(main.app) as client:
        body = client.get("/health").json()
    assert body["git_sha"] == "abc1234"


def test_health_sha_defaults_to_unknown(monkeypatch):
    monkeypatch.delenv("GIT_SHA", raising=False)
    with TestClient(main.app) as client:
        body = client.get("/health").json()
    assert body["git_sha"] == "unknown"