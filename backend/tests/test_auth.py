"""Tests for POST /auth/register, POST /auth/token, POST /auth/refresh, GET /auth/me."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


# ── Registration ─────────────────────────────────────────────────────────────

def test_register_returns_token_pair(client: TestClient):
    response = client.post(
        "/api/v1/auth/register",
        json={"full_name": "Alice Rwanda", "email": "alice@example.com", "password": "SecurePass1234"},
    )
    assert response.status_code == 201
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


def test_register_duplicate_email_returns_409(client: TestClient):
    payload = {"full_name": "Bob", "email": "bob@example.com", "password": "SecurePass1234"}
    client.post("/api/v1/auth/register", json=payload)
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409


def test_register_email_is_case_insensitive(client: TestClient):
    client.post(
        "/api/v1/auth/register",
        json={"full_name": "Carol", "email": "carol@example.com", "password": "SecurePass1234"},
    )
    response = client.post(
        "/api/v1/auth/register",
        json={"full_name": "Carol", "email": "CAROL@EXAMPLE.COM", "password": "SecurePass1234"},
    )
    assert response.status_code == 409


def test_register_short_password_rejected(client: TestClient):
    response = client.post(
        "/api/v1/auth/register",
        json={"full_name": "Dave", "email": "dave@example.com", "password": "short"},
    )
    assert response.status_code == 422


def test_register_invalid_email_rejected(client: TestClient):
    response = client.post(
        "/api/v1/auth/register",
        json={"full_name": "Eve", "email": "not-an-email", "password": "SecurePass1234"},
    )
    assert response.status_code == 422


# ── Login ────────────────────────────────────────────────────────────────────

def test_login_returns_token_pair(client: TestClient, citizen_user):
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "citizen@example.com", "password": "StrongPassword1234"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body


def test_login_wrong_password_returns_401(client: TestClient, citizen_user):
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "citizen@example.com", "password": "WrongPassword!"},
    )
    assert response.status_code == 401


def test_login_unknown_email_returns_401(client: TestClient):
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "nobody@example.com", "password": "DoesNotMatter1"},
    )
    assert response.status_code == 401


# ── Token refresh ────────────────────────────────────────────────────────────

def test_refresh_returns_new_token_pair(client: TestClient, citizen_user):
    login = client.post(
        "/api/v1/auth/token",
        data={"username": "citizen@example.com", "password": "StrongPassword1234"},
    )
    refresh_token = login.json()["refresh_token"]
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_refresh_with_access_token_rejected(client: TestClient, citizen_user):
    """Using the wrong token type for refresh should return 401."""
    login = client.post(
        "/api/v1/auth/token",
        data={"username": "citizen@example.com", "password": "StrongPassword1234"},
    )
    access_token = login.json()["access_token"]
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": access_token})
    assert response.status_code == 401


def test_refresh_with_garbage_token_rejected(client: TestClient):
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": "not.a.jwt"})
    assert response.status_code == 401


# ── /auth/me ─────────────────────────────────────────────────────────────────

def test_get_me_returns_current_user(client: TestClient, citizen_token: str):
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {citizen_token}"})
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "citizen@example.com"
    assert body["role"] == "citizen"
    assert "password_hash" not in body


def test_get_me_without_token_returns_401(client: TestClient):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_get_me_with_garbage_token_returns_401(client: TestClient):
    response = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer garbage"})
    assert response.status_code == 401
