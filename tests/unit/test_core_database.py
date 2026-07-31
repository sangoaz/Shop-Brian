"""
Tests de app/core/database.py.

Les tests d'intégration (tests/integration/) remplacent `get_session` via
`app.dependency_overrides` : ils n'exécutent donc jamais le vrai corps de
cette fonction. Ce module la teste directement pour s'assurer que le
générateur produit bien une session utilisable et se referme proprement.
"""

import pytest
from sqlmodel import Session

from app.core.database import engine, get_session

pytestmark = pytest.mark.unit


def test_engine_is_configured_from_settings():
    from app.core.config import settings

    assert str(engine.url) == settings.database_url


def test_get_session_yields_a_usable_session():
    session_generator = get_session()
    session = next(session_generator)

    assert isinstance(session, Session)

    # Simule la fermeture effectuée par FastAPI à la fin de la requête :
    # le générateur doit s'épuiser sans lever d'exception inattendue.
    with pytest.raises(StopIteration):
        next(session_generator)
