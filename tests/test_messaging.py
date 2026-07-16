from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_messaging_requires_auth():
    r = client.get("/api/v1/messaging/conversations")
    assert r.status_code in (401, 403)

def test_metrics_endpoint():
    r = client.get("/metrics")
    # Should return prometheus or json fallback
    assert r.status_code == 200
