from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_discovery_requires_auth():
    r = client.get("/api/v1/discovery/feed")
    assert r.status_code in (401, 403)

def test_health_detailed():
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert "checks" in data
    assert "database" in data["checks"]
