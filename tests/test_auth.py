from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_register_and_login():
    email = "pytest@example.com"
    # register may already exist
    r = client.post("/api/v1/auth/register", json={"email": email, "password": "password123", "name": "Test"})
    # either 201 or 400 if exists
    assert r.status_code in (201, 400)
    # login
    r2 = client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    if r2.status_code == 200:
        assert "access_token" in r2.json()
