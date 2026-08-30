"""Tests for GET /services — public catalogue endpoint."""

from fastapi.testclient import TestClient


def test_list_services_requires_no_auth(client: TestClient):
    """Services catalogue is public — no token needed."""
    response = client.get("/api/v1/services")
    assert response.status_code == 200


def test_list_services_returns_active_services(client: TestClient):
    response = client.get("/api/v1/services")
    services = response.json()
    assert isinstance(services, list)
    assert len(services) >= 1


def test_list_services_shape(client: TestClient):
    """Every service item must expose the fields the frontend relies on."""
    response = client.get("/api/v1/services")
    for service in response.json():
        assert "id" in service
        assert "code" in service
        assert "name" in service
        assert "description" in service


def test_business_registration_service_present(client: TestClient):
    response = client.get("/api/v1/services")
    codes = [s["code"] for s in response.json()]
    assert "business-registration" in codes
