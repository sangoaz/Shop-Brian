"""
Fixtures partagées pour l'ensemble de la suite de tests.

Ce module centralise :

- la configuration de l'environnement de test. Les variables d'environnement
  sont définies AVANT le premier import d'un module de `app`, car
  `app.core.config.settings` est un singleton instancié une seule fois au
  chargement du module. Si on les définissait après un import, ces valeurs
  seraient ignorées et les tests tenteraient d'utiliser la vraie base de
  données du projet ;
- une base de données SQLite en mémoire, recréée intégralement pour chaque
  test (aucun test ne doit dépendre de données laissées par un autre) ;
- un `TestClient` FastAPI dont la dépendance `get_session` est remplacée par
  la session de test, pour ne jamais toucher à la vraie base ;
- des "factories" légères qui créent et persistent un objet valide (User,
  Collection, Clothing) en un appel, avec des valeurs par défaut réalistes
  surchargeables via `**kwargs`.
"""

from __future__ import annotations

import os

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("SECRET_KEY", "test-secret-key-do-not-use-in-production")

from datetime import datetime, timezone
from typing import Callable

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

# Force l'enregistrement de tous les modèles SQLModel avant `create_all`
# (voir la docstring de app/models/__init__.py : sans cet import, les
# classes liées uniquement via TYPE_CHECKING n'apparaissent jamais dans
# SQLModel.metadata).
import app.models  # noqa: F401
from app.core.database import get_session
from app.core.security import create_access_token, hash_password
from app.enums import Item, Size, UserRole
from app.main import app
from app.models.clothes import Clothing
from app.models.collections import Collection
from app.models.user import User


@pytest.fixture(name="session")
def session_fixture():
    """
    Fournit une `Session` SQLModel connectée à une base SQLite en mémoire,
    recréée de zéro pour ce test uniquement.

    `StaticPool` force SQLAlchemy à réutiliser la même connexion physique
    pour toute la durée du test : sans cela, une base SQLite `sqlite://`
    ouvrirait une nouvelle connexion (donc une nouvelle base vide) à chaque
    requête, et les tables créées disparaîtraient immédiatement.

    On crée un moteur dédié par test (plutôt que de réutiliser celui de
    `app.core.database`) pour garantir une base vierge et isolée à chaque
    fois. On l'élimine explicitement via `engine.dispose()` en fin de test :
    `StaticPool` garde sa connexion sqlite ouverte tant que le moteur n'est
    pas disposé, ce qui sinon déclenche un `ResourceWarning: unclosed
    database` détecté par le garbage collector à la fin de la suite.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    engine.dispose()


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """
    `TestClient` FastAPI pour les tests d'intégration HTTP.

    La dépendance `get_session` de l'application est remplacée par une
    fonction qui retourne la session de test, afin que les requêtes passant
    par le client utilisent la base SQLite en mémoire au lieu de la base
    réelle configurée dans `app.core.config.settings`.
    """

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Factories
#
# Chaque factory persiste immédiatement l'objet (add + commit + refresh) et
# le retourne avec son id généré, prêt à être utilisé dans une assertion ou
# une requête HTTP.
# ---------------------------------------------------------------------------


@pytest.fixture
def user_factory(session: Session) -> Callable[..., User]:
    """Retourne une fonction créant un `User` de test (admin actif par défaut)."""

    def _make_user(**overrides) -> User:
        defaults = {
            "email": "admin@example.com",
            "password_hash": hash_password("SuperSecret123"),
            "role": UserRole.ADMIN,
            "is_active": True,
        }
        defaults.update(overrides)
        user = User(**defaults)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    return _make_user


@pytest.fixture
def collection_factory(session: Session) -> Callable[..., Collection]:
    """Retourne une fonction créant une `Collection` de test."""

    def _make_collection(**overrides) -> Collection:
        defaults = {
            "name": "Collection Été",
            "start": datetime.now(timezone.utc),
            "is_published": True,
        }
        defaults.update(overrides)
        collection = Collection(**defaults)
        session.add(collection)
        session.commit()
        session.refresh(collection)
        return collection

    return _make_collection


@pytest.fixture
def clothing_factory(session: Session) -> Callable[..., Clothing]:
    """Retourne une fonction créant un `Clothing` de test rattaché à une collection."""

    def _make_clothing(collection_id: int, **overrides) -> Clothing:
        defaults = {
            "name": "T-shirt basique",
            "item": Item.T_SHIRT,
            "size": Size.M,
            "price": 19.99,
            "description": "Un t-shirt en coton bio",
            "stock": 10,
        }
        defaults.update(overrides)
        clothing = Clothing(collection_id=collection_id, **defaults)
        session.add(clothing)
        session.commit()
        session.refresh(clothing)
        return clothing

    return _make_clothing


@pytest.fixture
def admin_user(user_factory: Callable[..., User]) -> User:
    """Un administrateur actif, prêt à s'authentifier."""
    return user_factory()


@pytest.fixture
def auth_headers(admin_user: User) -> dict[str, str]:
    """
    En-tête `Authorization: Bearer <token>` valide pour `admin_user`.

    On appelle directement `create_access_token` plutôt que de passer par
    `POST /auth/login`, pour ne pas coupler chaque test métier au flux de
    connexion complet (celui-ci est testé séparément dans
    test_routes_auth.py).
    """
    token = create_access_token(
        data={"sub": str(admin_user.id), "role": admin_user.role.value}
    )
    return {"Authorization": f"Bearer {token}"}
