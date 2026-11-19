from fastapi.testclient import TestClient

from app.main import app


def test_healthz():
    assert TestClient(app).get("/healthz").json() == {"status": "ok"}


def test_requires_user():
    assert TestClient(app).get("/jobs").status_code == 401
