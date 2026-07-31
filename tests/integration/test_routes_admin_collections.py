"""
Tests d'intégration de app/routes/admin/admin_collections.py.

Toutes les routes de ce module sont protégées par `require_admin` : chaque
groupe de tests vérifie d'abord le cas nominal (utilisateur admin
authentifié), puis le rejet sans authentification.
"""

from datetime import datetime, timedelta, timezone

import pytest

pytestmark = pytest.mark.integration


def test_create_collection_requires_authentication(client):
    response = client.post("/admin/collections", json={"name": "Été 2026", "start": "2026-06-01T00:00:00Z"})

    assert response.status_code == 401


def test_create_collection_as_admin_returns_201(client, auth_headers):
    response = client.post(
        "/admin/collections",
        json={"name": "Été 2026", "start": "2026-06-01T00:00:00Z"},
        headers=auth_headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Été 2026"
    assert body["is_published"] is True
    assert "id" in body


def test_list_collections_returns_created_collections(client, auth_headers, collection_factory):
    collection_factory(name="Ancienne", created_at=datetime.now(timezone.utc) - timedelta(days=1))
    collection_factory(name="Récente", created_at=datetime.now(timezone.utc))

    response = client.get("/admin/collections", headers=auth_headers)

    assert response.status_code == 200
    names = [item["name"] for item in response.json()]
    # La route trie par created_at décroissant : la plus récente arrive en
    # premier.
    assert names == ["Récente", "Ancienne"]


def test_list_collections_limit_is_capped_at_20(client, auth_headers):
    response = client.get("/admin/collections?limit=21", headers=auth_headers)

    # `limit` a une contrainte `le=20` côté route : au-delà, FastAPI répond
    # 422 avant même d'exécuter la requête SQL.
    assert response.status_code == 422


def test_get_collection_by_id(client, auth_headers, collection_factory):
    collection = collection_factory(name="Printemps 2026")

    response = client.get(f"/admin/collections/{collection.id}", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["id"] == collection.id


def test_get_collection_returns_404_when_missing(client, auth_headers):
    response = client.get("/admin/collections/999", headers=auth_headers)

    assert response.status_code == 404


def test_get_collection_without_an_end_date_is_serialized_correctly(
    client, auth_headers, collection_factory
):
    # Régression : `Collection.end` est optionnel côté modèle (une
    # collection peut ne pas encore avoir de date de fin), le schéma de
    # réponse doit donc accepter `end=None` sans lever une
    # ResponseValidationError (500).
    collection = collection_factory(name="Sans date de fin", end=None)

    response = client.get(f"/admin/collections/{collection.id}", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["end"] is None


def test_update_collection_only_changes_provided_fields(client, auth_headers, collection_factory):
    collection = collection_factory(name="Nom initial", is_published=True)

    response = client.patch(
        f"/admin/collections/{collection.id}",
        json={"name": "Nom modifié"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Nom modifié"
    # is_published n'était pas dans le payload : il doit rester inchangé
    # grâce à `exclude_unset=True` dans la route.
    assert body["is_published"] is True


def test_update_collection_returns_404_when_missing(client, auth_headers):
    response = client.patch(
        "/admin/collections/999", json={"name": "Peu importe"}, headers=auth_headers
    )

    assert response.status_code == 404
