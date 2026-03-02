import os
import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    monkeypatch.setenv("DB_PATH", ":memory:")
    monkeypatch.setenv("STROM_AUTH_MODE", "dev")

def test_health():
    with TestClient(app) as client:
        res = client.get("/api/v1/health")
        assert res.status_code == 200
        assert res.json() == {"status": "ok"}

def test_metrics():
    with TestClient(app) as client:
        res = client.get("/api/v1/metrics")
        assert res.status_code == 200

def test_dev_auth_missing_header():
    with TestClient(app) as client:
        res = client.get("/api/v1/me")
        assert res.status_code == 401
        assert "missing" in res.json()["detail"]

def test_dev_auth_flow():
    with TestClient(app) as client:
        email = "test@example.com"
        
        # First seen -> creates user
        res1 = client.get("/api/v1/me", headers={"x-dev-user-email": email})
        assert res1.status_code == 200
        data1 = res1.json()
        assert data1["email"] == email
        
        # Second request -> retrieves user
        res2 = client.get("/api/v1/me", headers={"x-dev-user-email": email})
        assert res2.status_code == 200
        data2 = res2.json()
        assert data1["id"] == data2["id"]

def test_prod_mode_disabled_dev_auth(monkeypatch):
    monkeypatch.setenv("STROM_AUTH_MODE", "prod")
    with TestClient(app) as client:
        res = client.get("/api/v1/me", headers={"x-dev-user-email": "test@example.com"})
        assert res.status_code == 500
        assert "disabled" in res.json()["detail"]
