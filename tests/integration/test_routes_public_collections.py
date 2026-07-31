"""
Tests d'intégration de app/routes/public/public_collections.py.

Contrairement aux routes /admin, ces routes ne demandent aucune
authentification, mais elles cachent les collections non publiées : c'est
ce filtrage qui est le comportement le plus important à couvrir ici (une
collection non publiée ne doit être visible ni dans la liste, ni via son
id direct — sinon on pourrait "deviner" son existence).
"""

from datetime import datetime, timedelta, timezone

import pytest

pytestmark = pytest.mark.integration


def test_list_public_collections_does_not_require_authentication(client):
    response = client.get("/collections/")

    assert response.status_code == 200


def test_list_public_collections_only_returns_published(client, collection_factory):
    collection_factory(name="Visible", is_published=True)
    collection_factory(name="Brouillon", is_published=False)

    response = client.get("/collections/")

    names = [item["name"] for item in response.json()]
    assert names == ["Visible"]


def test_list_public_collections_orders_by_created_at_desc(client, collection_factory):
    collection_factory(name="Ancienne", created_at=datetime.now(timezone.utc) - timedelta(days=1))
    collection_factory(name="Récente", created_at=datetime.now(timezone.utc))

    response = client.get("/collections/")

    names = [item["name"] for item in response.json()]
    assert names == ["Récente", "Ancienne"]


def test_list_public_collections_limit_is_capped_at_20(client):
    response = client.get("/collections/?limit=21")

    assert response.status_code == 422


def test_get_public_collection_returns_a_published_collection(client, collection_factory):
    collection = collection_factory(name="Été 2026", is_published=True)

    response = client.get(f"/collections/{collection.id}")

    assert response.status_code == 200
    assert response.json()["name"] == "Été 2026"


def test_get_public_collection_returns_404_for_an_unpublished_collection(
    client, collection_factory
):
    # La collection existe bel et bien, mais elle est en brouillon : le
    # comportement attendu côté public est identique à une collection qui
    # n'existe pas du tout (404), pour ne rien laisser fuiter.
    collection = collection_factory(name="Brouillon", is_published=False)

    response = client.get(f"/collections/{collection.id}")

    assert response.status_code == 404


def test_get_public_collection_returns_404_when_missing(client):
    response = client.get("/collections/999")

    assert response.status_code == 404
