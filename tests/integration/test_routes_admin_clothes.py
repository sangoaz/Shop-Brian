"""
Tests d'intégration de app/routes/admin/admin_clothes.py.

Ces routes sont imbriquées sous une collection
(`/admin/collections/{collection_id}/clothing...`) et vérifient donc deux
niveaux d'existence : celle de la collection, puis celle du vêtement (voir
aussi tests/unit/test_utils_clothes.py pour la logique sous-jacente).
"""

import pytest

pytestmark = pytest.mark.integration


CLOTHING_PAYLOAD = {
    "name": "T-shirt basique",
    "item": "T_SHIRT",
    "size": "M",
    "price": 19.99,
    "description": "Un t-shirt en coton bio",
    "stock": 10,
}


def test_create_clothing_requires_authentication(client, collection_factory):
    collection = collection_factory()

    response = client.post(
        f"/admin/collections/{collection.id}/clothing", json=CLOTHING_PAYLOAD
    )

    assert response.status_code == 401


def test_create_clothing_as_admin_returns_201(client, auth_headers, collection_factory):
    collection = collection_factory()

    response = client.post(
        f"/admin/collections/{collection.id}/clothing",
        json=CLOTHING_PAYLOAD,
        headers=auth_headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "T-shirt basique"
    assert body["stock"] == 10


def test_create_clothing_returns_404_when_collection_is_missing(client, auth_headers):
    response = client.post(
        "/admin/collections/999/clothing", json=CLOTHING_PAYLOAD, headers=auth_headers
    )

    assert response.status_code == 404


def test_list_clothes_for_a_collection(client, auth_headers, collection_factory, clothing_factory):
    collection = collection_factory()
    other_collection = collection_factory()
    clothing_factory(collection_id=collection.id, name="Short")
    clothing_factory(collection_id=other_collection.id, name="Ne doit pas apparaître")

    response = client.get(f"/admin/collections/{collection.id}/clothes", headers=auth_headers)

    assert response.status_code == 200
    names = [item["name"] for item in response.json()]
    assert names == ["Short"]


def test_get_clothing_by_id(client, auth_headers, collection_factory, clothing_factory):
    collection = collection_factory()
    clothing = clothing_factory(collection_id=collection.id, name="Veste")

    response = client.get(
        f"/admin/collections/{collection.id}/clothing/{clothing.id}", headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json()["id"] == clothing.id


def test_get_clothing_returns_404_for_wrong_collection(
    client, auth_headers, collection_factory, clothing_factory
):
    collection_a = collection_factory()
    collection_b = collection_factory()
    clothing = clothing_factory(collection_id=collection_a.id)

    response = client.get(
        f"/admin/collections/{collection_b.id}/clothing/{clothing.id}", headers=auth_headers
    )

    assert response.status_code == 404


def test_update_clothing_only_changes_provided_fields(
    client, auth_headers, collection_factory, clothing_factory
):
    collection = collection_factory()
    clothing = clothing_factory(collection_id=collection.id, stock=10, price=19.99)

    response = client.patch(
        f"/admin/collections/{collection.id}/clothing/{clothing.id}",
        json={"stock": 3},
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["stock"] == 3
    # price n'était pas dans le payload : il doit rester inchangé grâce à
    # `exclude_unset=True` dans la route.
    assert body["price"] == 19.99


def test_update_clothing_returns_404_when_missing(client, auth_headers, collection_factory):
    collection = collection_factory()

    response = client.patch(
        f"/admin/collections/{collection.id}/clothing/999",
        json={"stock": 1},
        headers=auth_headers,
    )

    assert response.status_code == 404
