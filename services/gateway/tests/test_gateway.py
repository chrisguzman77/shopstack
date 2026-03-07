from fastapi.testclient import TestClient

from gateway_service.api import app

client = TestClient(app)


def test_root_returns_service_links() -> None:
    r = client.get("/")
    assert r.status_code == 200

    data = r.json()
    assert "auth_docs" in data
    assert "orders_docs" in data
    assert "gateway_docs" in data