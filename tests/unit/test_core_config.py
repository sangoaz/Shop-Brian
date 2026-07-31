"""
Tests de app/core/config.py.

`settings` est un singleton chargé une seule fois au premier import (voir
conftest.py, qui fixe DATABASE_URL et SECRET_KEY avant tout import de
`app`). Ces tests documentent les valeurs par défaut attendues plutôt que
de re-tester `pydantic-settings` lui-même.
"""

import pytest

from app.core.config import settings

pytestmark = pytest.mark.unit


def test_secret_key_and_database_url_come_from_the_environment():
    # Ces deux champs n'ont pas de valeur par défaut dans Settings : ils
    # doivent obligatoirement provenir de l'environnement ou du .env.
    assert settings.secret_key == "test-secret-key-do-not-use-in-production"
    assert settings.database_url == "sqlite://"


def test_default_jwt_algorithm_is_hs256():
    assert settings.algorithm == "HS256"


def test_default_access_token_expiry_is_30_minutes():
    assert settings.access_token_expire_minutes == 30


def test_debug_defaults_to_false():
    assert settings.debug is False
