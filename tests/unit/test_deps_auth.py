"""
Tests de app/deps/auth.py : dépendances FastAPI `get_current_user` et
`require_admin`.

Ces fonctions sont décorées pour être utilisées via `Depends(...)` par
FastAPI, mais restent de simples fonctions Python : on peut les appeler
directement en fournissant `token`/`session`/`current_user` explicitement,
ce qui évite de passer par une vraie requête HTTP pour ces cas unitaires
(les tests d'intégration correspondants sont dans
tests/integration/test_routes_auth.py).
"""

from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.core.security import create_access_token
from app.deps.auth import get_current_user, require_admin

pytestmark = pytest.mark.unit


class TestGetCurrentUser:
    def test_returns_the_user_matching_a_valid_token(self, session, user_factory):
        user = user_factory()
        token = create_access_token(data={"sub": str(user.id)})

        result = get_current_user(token=token, session=session)

        assert result.id == user.id

    def test_rejects_an_invalid_token_with_401(self, session):
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token="not-a-valid-jwt", session=session)

        assert exc_info.value.status_code == 401

    def test_rejects_a_token_without_a_sub_claim_with_401(self, session):
        token = create_access_token(data={})  # pas de "sub"

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token=token, session=session)

        assert exc_info.value.status_code == 401

    def test_rejects_a_token_for_an_unknown_user_with_401(self, session):
        token = create_access_token(data={"sub": "999999"})

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token=token, session=session)

        assert exc_info.value.status_code == 401

    def test_rejects_an_inactive_user_with_403(self, session, user_factory):
        user = user_factory(is_active=False)
        token = create_access_token(data={"sub": str(user.id)})

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token=token, session=session)

        assert exc_info.value.status_code == 403


class TestRequireAdmin:
    def test_allows_an_admin_user_through(self, user_factory):
        admin = user_factory()  # role=ADMIN par défaut, voir conftest.py

        result = require_admin(current_user=admin)

        assert result is admin

    def test_rejects_a_non_admin_user_with_403(self):
        # UserRole ne définit aujourd'hui qu'une seule valeur (ADMIN), donc
        # aucun User "réel" ne peut avoir un autre rôle (voir test_enums.py::
        # TestUserRole::test_has_a_single_admin_role). On simule ici un futur
        # rôle non-admin avec un simple objet possédant l'attribut `role`
        # utilisé par `require_admin`, pour que ce test reste valable dès
        # qu'un second rôle sera ajouté à l'enum.
        non_admin = SimpleNamespace(role="CUSTOMER")

        with pytest.raises(HTTPException) as exc_info:
            require_admin(current_user=non_admin)

        assert exc_info.value.status_code == 403
