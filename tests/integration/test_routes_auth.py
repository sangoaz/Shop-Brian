"""
Tests d'intégration de app/routes/auth.py (POST /auth/login, GET /auth/me).

Ces tests passent par le vrai `TestClient` HTTP (fixture `client`), pour
vérifier le comportement de bout en bout : parsing du formulaire OAuth2,
génération du token, dépendance d'authentification, sérialisation de la
réponse.
"""

import pytest

from app.core.security import hash_password

pytestmark = pytest.mark.integration


def test_login_returns_a_bearer_token_for_valid_credentials(client, user_factory):
    user_factory(email="jane@example.com", password_hash=hash_password("CorrectHorse1"))

    response = client.post(
        "/auth/login",
        data={"username": "jane@example.com", "password": "CorrectHorse1"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str) and body["access_token"]


def test_login_rejects_a_wrong_password(client, user_factory):
    user_factory(email="jane@example.com", password_hash=hash_password("CorrectHorse1"))

    response = client.post(
        "/auth/login",
        data={"username": "jane@example.com", "password": "WrongPassword"},
    )

    assert response.status_code == 401


def test_login_rejects_an_unknown_email(client):
    response = client.post(
        "/auth/login",
        data={"username": "ghost@example.com", "password": "whatever"},
    )

    assert response.status_code == 401


def test_get_me_requires_a_bearer_token(client):
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_get_me_rejects_an_invalid_token(client):
    response = client.get(
        "/auth/me", headers={"Authorization": "Bearer not-a-real-token"}
    )

    assert response.status_code == 401


def test_get_me_returns_the_authenticated_user(client, admin_user, auth_headers):
    response = client.get("/auth/me", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == admin_user.id
    assert body["email"] == admin_user.email
    assert body["role"] == "ADMIN"
