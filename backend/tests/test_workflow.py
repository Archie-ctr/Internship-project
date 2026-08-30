"""Tests for the officer workflow: status transitions, review, audit trail."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.audit_log import AuditLog

VALID_PAYLOAD = {
    "business_name": "Workflow Test Ltd",
    "business_type": "limited_company",
    "owner": {"full_name": "Jane Doe", "id_number": "1234567890", "phone_number": "+250788000000"},
    "address": {"line1": "KG 7 Ave", "city": "Kigali", "district": "Gasabo", "country": "Rwanda"},
}


@pytest.fixture()
def submitted_application_id(client: TestClient, citizen_token: str) -> str:
    """Create a submitted application and return its ID."""
    response = client.post(
        "/api/v1/applications",
        json=VALID_PAYLOAD,
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    assert response.status_code == 201
    return response.json()["id"]


# ── Access control ────────────────────────────────────────────────────────────

def test_citizen_cannot_access_officer_dashboard(client: TestClient, citizen_token: str):
    response = client.get(
        "/api/v1/officer/applications",
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    assert response.status_code == 403


def test_officer_can_list_all_applications(
    client: TestClient, officer_token: str, submitted_application_id: str
):
    response = client.get(
        "/api/v1/officer/applications",
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert response.status_code == 200
    ids = [a["id"] for a in response.json()]
    assert submitted_application_id in ids


def test_officer_can_filter_by_status(
    client: TestClient, officer_token: str, submitted_application_id: str
):
    response = client.get(
        "/api/v1/officer/applications?status_filter=submitted",
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert response.status_code == 200
    for app in response.json():
        assert app["status"] == "submitted"


# ── State transitions ─────────────────────────────────────────────────────────

def test_officer_can_advance_submitted_to_under_review(
    client: TestClient, officer_token: str, submitted_application_id: str
):
    response = client.post(
        f"/api/v1/officer/applications/{submitted_application_id}/transition",
        json={"new_status": "under_review"},
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "under_review"


def test_illegal_transition_returns_422(
    client: TestClient, officer_token: str, submitted_application_id: str
):
    """Jumping from submitted directly to approved is not in the state machine."""
    response = client.post(
        f"/api/v1/officer/applications/{submitted_application_id}/transition",
        json={"new_status": "approved"},
        headers={"Authorization": f"Bearer {officer_token}"},
    )
    assert response.status_code == 422


def test_full_happy_path_workflow(
    client: TestClient, officer_token: str, submitted_application_id: str
):
    """Walk the entire state machine: submitted → … → completed."""
    headers = {"Authorization": f"Bearer {officer_token}"}
    app_id = submitted_application_id

    def transition(new_status: str):
        r = client.post(
            f"/api/v1/officer/applications/{app_id}/transition",
            json={"new_status": new_status},
            headers=headers,
        )
        assert r.status_code == 200, f"Transition to {new_status} failed: {r.json()}"
        return r.json()

    transition("under_review")
    transition("payment_pending")
    transition("paid")
    transition("officer_review")

    # Final review step uses the dedicated review endpoint.
    review = client.post(
        f"/api/v1/officer/applications/{app_id}/review",
        json={"decision": "approved"},
        headers=headers,
    )
    assert review.status_code == 200
    assert review.json()["status"] == "approved"
    assert review.json()["registration_number"] is not None

    transition("completed")


def test_rejection_requires_reason(
    client: TestClient, officer_token: str, submitted_application_id: str
):
    # Advance to officer_review first.
    headers = {"Authorization": f"Bearer {officer_token}"}
    for s in ["under_review", "payment_pending", "paid", "officer_review"]:
        client.post(
            f"/api/v1/officer/applications/{submitted_application_id}/transition",
            json={"new_status": s},
            headers=headers,
        )

    response = client.post(
        f"/api/v1/officer/applications/{submitted_application_id}/review",
        json={"decision": "rejected"},  # missing rejection_reason
        headers=headers,
    )
    assert response.status_code == 422


def test_rejection_stores_reason(
    client: TestClient, officer_token: str, submitted_application_id: str
):
    headers = {"Authorization": f"Bearer {officer_token}"}
    for s in ["under_review", "payment_pending", "paid", "officer_review"]:
        client.post(
            f"/api/v1/officer/applications/{submitted_application_id}/transition",
            json={"new_status": s},
            headers=headers,
        )

    response = client.post(
        f"/api/v1/officer/applications/{submitted_application_id}/review",
        json={"decision": "rejected", "rejection_reason": "Incomplete address"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["rejection_reason"] == "Incomplete address"


# ── Audit trail ───────────────────────────────────────────────────────────────

def test_audit_trail_grows_with_transitions(
    client: TestClient, officer_token: str, submitted_application_id: str, db: Session
):
    headers = {"Authorization": f"Bearer {officer_token}"}
    client.post(
        f"/api/v1/officer/applications/{submitted_application_id}/transition",
        json={"new_status": "under_review"},
        headers=headers,
    )
    response = client.get(
        f"/api/v1/officer/applications/{submitted_application_id}/audit",
        headers=headers,
    )
    assert response.status_code == 200
    # At least: application_created + status_transitioned
    assert len(response.json()) >= 2
