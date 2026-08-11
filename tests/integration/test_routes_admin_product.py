"""
Tests d'intégration de app/routes/admin/admin_product.py (anciennement
app/routes/admin/admin_clothes.py, renommé lors du passage à
Product/ProductVariant).

`Product` ne porte plus `size`/`stock` (déplacés vers `ProductVariant`, voir
tests/integration/test_routes_admin_product_variant.py) : les payloads et
assertions ci-dessous reflètent ce périmètre réduit.

Ces routes sont imbriquées sous une collection
(`/admin/collections/{collection_id}/products...`) et vérifient donc deux
niveaux d'existence : celle de la collection, puis celle du produit (voir
aussi tests/unit/test_utils_product.py pour la logique sous-jacente).
"""

import pytest

pytestmark = pytest.mark.integration


PRODUCT_PAYLOAD = {
    "name": "T-shirt basique",
    "item": "T_SHIRT",
    "description": "Un t-shirt en coton bio",
    "price": 19.99,
}


def test_create_product_requires_authentication(client, collection_factory):
    collection = collection_factory()

    response = client.post(
        f"/admin/collections/{collection.id}/products", json=PRODUCT_PAYLOAD
    )

    assert response.status_code == 401


def test_create_product_as_admin_returns_201(client, auth_headers, collection_factory):
    collection = collection_factory()

    response = client.post(
        f"/admin/collections/{collection.id}/products",
        json=PRODUCT_PAYLOAD,
        headers=auth_headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "T-shirt basique"
    assert body["price"] == 19.99
    # `size` et `stock` n'existent plus sur Product : ils ne doivent pas
    # apparaître dans la réponse.
    assert "size" not in body
    assert "stock" not in body


def test_create_product_returns_404_when_collection_is_missing(client, auth_headers):
    response = client.post(
        "/admin/collections/999/products", json=PRODUCT_PAYLOAD, headers=auth_headers
    )

    assert response.status_code == 404


def test_list_products_for_a_collection(client, auth_headers, collection_factory, product_factory):
    collection = collection_factory()
    other_collection = collection_factory()
    product_factory(collection_id=collection.id, name="Short")
    product_factory(collection_id=other_collection.id, name="Ne doit pas apparaître")

    response = client.get(f"/admin/collections/{collection.id}/products", headers=auth_headers)

    assert response.status_code == 200
    names = [item["name"] for item in response.json()]
    assert names == ["Short"]


def test_get_product_by_id(client, auth_headers, collection_factory, product_factory):
    collection = collection_factory()
    product = product_factory(collection_id=collection.id, name="Veste")

    response = client.get(
        f"/admin/collections/{collection.id}/products/{product.id}", headers=auth_headers
    )

    assert response.status_code == 200
    assert response.json()["id"] == product.id


def test_get_product_returns_404_for_wrong_collection(
    client, auth_headers, collection_factory, product_factory
):
    collection_a = collection_factory()
    collection_b = collection_factory()
    product = product_factory(collection_id=collection_a.id)

    response = client.get(
        f"/admin/collections/{collection_b.id}/products/{product.id}", headers=auth_headers
    )

    assert response.status_code == 404


def test_update_product_only_changes_provided_fields(
    client, auth_headers, collection_factory, product_factory
):
    collection = collection_factory()
    product = product_factory(collection_id=collection.id, name="Nom initial", price=19.99)

    response = client.patch(
        f"/admin/collections/{collection.id}/products/{product.id}",
        json={"price": 24.99},
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["price"] == 24.99
    # name n'était pas dans le payload : il doit rester inchangé grâce à
    # `exclude_unset=True` dans la route.
    assert body["name"] == "Nom initial"


def test_update_product_returns_404_when_missing(client, auth_headers, collection_factory):
    collection = collection_factory()

    response = client.patch(
        f"/admin/collections/{collection.id}/products/999",
        json={"price": 1},
        headers=auth_headers,
    )

    assert response.status_code == 404
