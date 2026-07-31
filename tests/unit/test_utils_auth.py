"""
Tests de app/utils/auth.py : authentification et helper d'erreur.
"""

import pytest
from fastapi import HTTPException

from app.utils.auth import authenticate_user, invalid_credentials

pytestmark = pytest.mark.unit


class TestAuthenticateUser:
    def test_returns_the_user_when_credentials_are_correct(self, session, user_factory):
        from app.core.security import hash_password

        user = user_factory(
            email="jane@example.com", password_hash=hash_password("CorrectHorse1")
        )

        result = authenticate_user(session, "jane@example.com", "CorrectHorse1")

        assert result is not None
        assert result.id == user.id

    def test_returns_none_when_the_password_is_wrong(self, session, user_factory):
        user_factory(email="jane@example.com")

        result = authenticate_user(session, "jane@example.com", "WrongPassword")

        assert result is None

    def test_returns_none_when_the_email_is_unknown(self, session):
        result = authenticate_user(session, "ghost@example.com", "whatever")

        assert result is None

    def test_returns_none_for_an_inactive_account(self, session, user_factory):
        from app.core.security import hash_password

        user_factory(
            email="jane@example.com",
            password_hash=hash_password("CorrectHorse1"),
            is_active=False,
        )

        # Le mot de passe est correct, mais le compte est désactivé : la
        # connexion doit tout de même être refusée.
        result = authenticate_user(session, "jane@example.com", "CorrectHorse1")

        assert result is None


class TestInvalidCredentials:
    def test_raises_a_401_with_bearer_challenge_header(self):
        with pytest.raises(HTTPException) as exc_info:
            invalid_credentials()

        assert exc_info.value.status_code == 401
        assert exc_info.value.headers["WWW-Authenticate"] == "Bearer"
