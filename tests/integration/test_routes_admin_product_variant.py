"""
Tests d'intégration de app/routes/admin/admin_product_variant.py.

Ces routes sont imbriquées à trois niveaux
(`/admin/collections/{collection_id}/products/{product_id}/variants...`) :
`get_variant_or_404` vérifie en cascade que la collection existe, puis le
produit, puis la variante elle-même (voir aussi
tests/unit/test_utils_product_variant.py pour la logique sous-jacente).
"""

import pytest

pytestmark = pytest.mark.integration


VARIANT_PAYLOAD = {
    "size": "M",
    "stock": 15,
    "sku": "SKU-TEST-001",
}


def test_create_variant_requires_authentication(client, collection_factory, product_factory):
    collection = collection_factory()
    product = product_factory(collection_id=collection.id)

    response = client.post(
        f"/admin/collections/{collection.id}/products/{product.id}/variants",
        json=VARIANT_PAYLOAD,
    )

    assert response.status_code == 401


def test_create_variant_as_admin_returns_201(
    client, auth_headers, collection_factory, product_factory
):
    collection = collection_factory()
    product = product_factory(collection_id=collection.id)

    response = client.post(
        f"/admin/collections/{collection.id}/products/{product.id}/variants",
        json=VARIANT_PAYLOAD,
        headers=auth_headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["sku"] == "SKU-TEST-001"
    assert body["stock"] == 15
    assert body["price_override"] is None
    assert body["is_expired"] is False


def test_create_variant_returns_404_when_product_is_missing(
    client, auth_headers, collection_factory
):
    collection = collection_factory()

    response = client.post(
        f"/admin/collections/{collection.id}/products/999/variants",
        json=VARIANT_PAYLOAD,
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_create_variant_returns_404_when_collection_is_missing(client, auth_headers):
    response = client.post(
        "/admin/collections/999/products/1/variants",
        json=VARIANT_PAYLOAD,
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_list_variants_for_a_product(
    client, auth_headers, collection_factory, product_factory, variant_factory
):
    collection = collection_factory()
    product = product_factory(collection_id=collection.id)
    other_product = product_factory(collection_id=collection.id)
    variant_factory(product_id=product.id, sku="SKU-A")
    variant_factory(product_id=other_product.id, sku="SKU-B")

    response = client.get(
        f"/admin/collections/{collection.id}/products/{product.id}/variants",
        headers=auth_headers,
    )

    assert response.status_code == 200
    skus = [item["sku"] for item in response.json()]
    assert skus == ["SKU-A"]


def test_get_variant_by_id(
    client, auth_headers, collection_factory, product_factory, variant_factory
):
    collection = collection_factory()
    product = product_factory(collection_id=collection.id)
    variant = variant_factory(product_id=product.id, sku="SKU-A")

    response = client.get(
        f"/admin/collections/{collection.id}/products/{product.id}/variants/{variant.id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == variant.id


def test_get_variant_returns_404_for_wrong_product(
    client, auth_headers, collection_factory, product_factory, variant_factory
):
    collection = collection_factory()
    product_a = product_factory(collection_id=collection.id)
    product_b = product_factory(collection_id=collection.id)
    variant = variant_factory(product_id=product_a.id, sku="SKU-A")

    response = client.get(
        f"/admin/collections/{collection.id}/products/{product_b.id}/variants/{variant.id}",
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_update_variant_only_changes_provided_fields(
    client, auth_headers, collection_factory, product_factory, variant_factory
):
    collection = collection_factory()
    product = product_factory(collection_id=collection.id)
    variant = variant_factory(product_id=product.id, sku="SKU-A", stock=10)

    response = client.patch(
        f"/admin/collections/{collection.id}/products/{product.id}/variants/{variant.id}",
        json={"stock": 3},
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["stock"] == 3
    # sku n'était pas dans le payload : il doit rester inchangé grâce à
    # `exclude_unset=True` dans la route.
    assert body["sku"] == "SKU-A"


def test_update_variant_can_mark_it_as_expired(
    client, auth_headers, collection_factory, product_factory, variant_factory
):
    collection = collection_factory()
    product = product_factory(collection_id=collection.id)
    variant = variant_factory(product_id=product.id, sku="SKU-A", is_expired=False)

    response = client.patch(
        f"/admin/collections/{collection.id}/products/{product.id}/variants/{variant.id}",
        json={"is_expired": True},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["is_expired"] is True


def test_update_variant_returns_404_when_missing(
    client, auth_headers, collection_factory, product_factory
):
    collection = collection_factory()
    product = product_factory(collection_id=collection.id)

    response = client.patch(
        f"/admin/collections/{collection.id}/products/{product.id}/variants/999",
        json={"stock": 1},
        headers=auth_headers,
    )

    assert response.status_code == 404
