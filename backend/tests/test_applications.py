"""Tests for citizen application endpoints and RBAC enforcement."""

import pytest
from fastapi.testclient import TestClient


VALID_PAYLOAD = {
    "business_name": "Rwanda Tech Ltd",
    "business_type": "limited_company",
    "owner": {"full_name": "Jane Doe", "id_number": "1234567890", "phone_number": "+250788000000"},
    "address": {"line1": "KG 7 Ave", "city": "Kigali", "district": "Gasabo", "country": "Rwanda"},
}


# ── Create application ────────────────────────────────────────────────────────

def test_citizen_can_create_application(client: TestClient, citizen_token: str):
    response = client.post(
        "/api/v1/applications",
        json=VALID_PAYLOAD,
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "submitted"
    assert body["business_name"] == "Rwanda Tech Ltd"
    assert body["service_code"] == "business-registration"


def test_create_application_without_token_returns_401(client: TestClient):
    response = client.post("/api/v1/applications", json=VALID_PAYLOAD)
    assert response.status_code == 401


def test_officer_cannot_create_application(client: TestClient, officer_token: str):
    """Officers are not citizens; the role check must return 403."""
    response = client.post(
        "/api/v1/applications",
        json=VALID_PAYLOAD,
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert response.status_code == 403


def test_create_application_missing_business_name_returns_422(client: TestClient, citizen_token: str):
    bad_payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "business_name"}
    response = client.post(
        "/api/v1/applications",
        json=bad_payload,
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    assert response.status_code == 422


def test_create_application_invalid_business_type_returns_422(client: TestClient, citizen_token: str):
    payload = {**VALID_PAYLOAD, "business_type": "unknown_type"}
    response = client.post(
        "/api/v1/applications",
        json=payload,
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    assert response.status_code == 422


# ── List own applications ─────────────────────────────────────────────────────

def test_citizen_can_list_own_applications(client: TestClient, citizen_token: str):
    # Create one application first.
    client.post(
        "/api/v1/applications",
        json=VALID_PAYLOAD,
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    response = client.get(
        "/api/v1/applications/me",
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1


def test_list_applications_without_token_returns_401(client: TestClient):
    response = client.get("/api/v1/applications/me")
    assert response.status_code == 401


def test_citizens_see_only_their_own_applications(
    client: TestClient, citizen_token: str, db
):
    """A second citizen's applications must not appear in the first citizen's list."""
    from app.models.role import Role
    from app.models.user import User
    from app.core.security import hash_password

    role = db.query(Role).filter(Role.name == "citizen").first()
    other = User(
        email="other@example.com",
        full_name="Other User",
        password_hash=hash_password("StrongPassword1234"),
        role=role,
    )
    db.add(other)
    db.flush()

    # Log in as the second citizen and create an application.
    other_login = client.post(
        "/api/v1/auth/token",
        data={"username": "other@example.com", "password": "StrongPassword1234"},
    )
    other_token = other_login.json()["access_token"]
    client.post(
        "/api/v1/applications",
        json={**VALID_PAYLOAD, "business_name": "Other Corp"},
        headers={"Authorization": f"Bearer {other_token}"},
    )

    # First citizen's list must be empty.
    response = client.get(
        "/api/v1/applications/me",
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    assert response.status_code == 200
    assert len(response.json()) == 0


# ── Application detail ────────────────────────────────────────────────────────

def test_citizen_can_get_own_application_detail(client: TestClient, citizen_token: str):
    create = client.post(
        "/api/v1/applications",
        json=VALID_PAYLOAD,
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    app_id = create.json()["id"]
    response = client.get(
        f"/api/v1/applications/{app_id}",
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == app_id
    assert "form_data" in body


def test_citizen_cannot_access_another_citizens_application(
    client: TestClient, citizen_token: str, db
):
    from app.models.role import Role
    from app.models.user import User
    from app.core.security import hash_password

    role = db.query(Role).filter(Role.name == "citizen").first()
    other = User(
        email="snooper@example.com",
        full_name="Snooper",
        password_hash=hash_password("StrongPassword1234"),
        role=role,
    )
    db.add(other)
    db.flush()

    other_login = client.post(
        "/api/v1/auth/token",
        data={"username": "snooper@example.com", "password": "StrongPassword1234"},
    )
    other_token = other_login.json()["access_token"]

    # Snooper creates their own application.
    create = client.post(
        "/api/v1/applications",
        json={**VALID_PAYLOAD, "business_name": "Snooper Corp"},
        headers={"Authorization": f"Bearer {other_token}"},
    )
    snooper_app_id = create.json()["id"]

    # First citizen tries to read snooper's application — must get 404 (not 403,
    # to avoid revealing whether the ID exists at all).
    response = client.get(
        f"/api/v1/applications/{snooper_app_id}",
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    assert response.status_code == 404


# ── Audit log ─────────────────────────────────────────────────────────────────

def test_audit_log_created_on_application_submit(client: TestClient, citizen_token: str, db):
    from app.models.audit_log import AuditLog

    response = client.post(
        "/api/v1/applications",
        json=VALID_PAYLOAD,
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    app_id = response.json()["id"]

    logs = db.query(AuditLog).filter(AuditLog.application_id == app_id).all()
    assert len(logs) >= 1
    assert logs[0].action == "application_created"
    assert logs[0].to_state == "submitted"
