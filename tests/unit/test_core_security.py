"""
Tests de app/core/security.py : hachage de mot de passe et JWT.

Le hachage (bcrypt via passlib) et l'encodage JWT (python-jose) sont des
bibliothèques tierces déjà largement testées : on ne teste pas leur
implémentation, mais le comportement observable de nos deux petites
fonctions wrapper (`hash_password`/`verify_password`,
`create_access_token`/`decode_access_token`), notamment les cas d'erreur.
"""

from datetime import timedelta

import pytest

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

pytestmark = pytest.mark.unit


class TestPasswordHashing:
    def test_hash_is_not_the_plain_password(self):
        assert hash_password("SuperSecret123") != "SuperSecret123"

    def test_same_password_produces_different_hashes(self):
        # bcrypt génère un sel aléatoire à chaque appel : deux hachages du
        # même mot de passe ne doivent jamais être identiques. Si ce test
        # échoue, c'est probablement le signe que le sel n'est plus généré
        # correctement (ex: schéma bcrypt mal configuré).
        assert hash_password("SuperSecret123") != hash_password("SuperSecret123")

    def test_verify_password_accepts_the_correct_password(self):
        hashed = hash_password("SuperSecret123")
        assert verify_password("SuperSecret123", hashed) is True

    def test_verify_password_rejects_a_wrong_password(self):
        hashed = hash_password("SuperSecret123")
        assert verify_password("WrongPassword", hashed) is False


class TestAccessTokens:
    def test_decode_returns_the_data_used_to_create_the_token(self):
        token = create_access_token(data={"sub": "42", "role": "ADMIN"})
        payload = decode_access_token(token)

        assert payload is not None
        assert payload["sub"] == "42"
        assert payload["role"] == "ADMIN"

    def test_token_carries_an_expiry_claim(self):
        token = create_access_token(data={"sub": "42"})
        payload = decode_access_token(token)

        assert "exp" in payload

    def test_decode_rejects_a_malformed_token(self):
        assert decode_access_token("this-is-not-a-jwt") is None

    def test_decode_rejects_an_expired_token(self):
        # On force une expiration dans le passé pour vérifier que
        # `decode_access_token` renvoie None plutôt que de lever une
        # exception non gérée jusqu'à l'appelant.
        expired_token = create_access_token(
            data={"sub": "42"}, expires_delta=timedelta(seconds=-1)
        )
        assert decode_access_token(expired_token) is None

    def test_decode_rejects_a_token_signed_with_a_different_key(self):
        from jose import jwt as jose_jwt

        token_signed_elsewhere = jose_jwt.encode(
            {"sub": "42"}, "a-completely-different-secret", algorithm="HS256"
        )
        assert decode_access_token(token_signed_elsewhere) is None
