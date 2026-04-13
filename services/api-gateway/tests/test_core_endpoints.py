from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_version_endpoint() -> None:
    response = client.get("/v1/version")
    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "api-gateway"
    assert payload["api_version"] == "v1"
