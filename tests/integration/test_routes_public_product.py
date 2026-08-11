"""
Tests d'intégration de app/routes/public/public_product.py
(GET /products, GET /products/{product_id}).

Ce module remplace à la fois l'ancienne route publique "tous les vêtements"
(GET /clothes/) et la route imbriquée "vêtements d'une collection"
(GET /collections/{collection_id}/clothes, supprimée) : on filtre
maintenant par collection via le paramètre de requête optionnel
`?collection_id=` plutôt que par un segment d'URL.

Un produit n'est visible que s'il est publié et rattaché à une collection
publiée (voir `visible_product_statement` dans app/utils/product.py, testée
aussi côté unitaire dans tests/unit/test_utils_product.py). La réponse
publique embarque en plus la liste des variantes (`PublicVariantRead`), dont
le prix est calculé (`effective_price` : le prix de base du produit, sauf
surcharge par variante).
"""

import pytest

pytestmark = pytest.mark.integration


def test_list_public_products_does_not_require_authentication(client):
    response = client.get("/products")

    assert response.status_code == 200


def test_list_public_products_excludes_unpublished_products(
    client, collection_factory, product_factory
):
    collection = collection_factory(is_published=True)
    product_factory(collection_id=collection.id, name="En vente", is_published=True)
    product_factory(collection_id=collection.id, name="Brouillon", is_published=False)

    response = client.get("/products")

    names = [item["name"] for item in response.json()]
    assert names == ["En vente"]


def test_list_public_products_excludes_products_from_an_unpublished_collection(
    client, collection_factory, product_factory
):
    published_collection = collection_factory(is_published=True)
    draft_collection = collection_factory(is_published=False)
    product_factory(collection_id=published_collection.id, name="Visible")
    product_factory(collection_id=draft_collection.id, name="Caché", is_published=True)

    response = client.get("/products")

    names = [item["name"] for item in response.json()]
    assert names == ["Visible"]


def test_list_public_products_can_be_filtered_by_collection(
    client, collection_factory, product_factory
):
    collection_a = collection_factory(is_published=True)
    collection_b = collection_factory(is_published=True)
    product_factory(collection_id=collection_a.id, name="Dans A")
    product_factory(collection_id=collection_b.id, name="Dans B")

    response = client.get(f"/products?collection_id={collection_a.id}")

    names = [item["name"] for item in response.json()]
    assert names == ["Dans A"]


def test_list_public_products_limit_is_capped_at_20(client):
    response = client.get("/products?limit=21")

    assert response.status_code == 422


def test_public_product_read_does_not_expose_internal_fields(
    client, collection_factory, product_factory
):
    # `PublicProductRead` est volontairement plus restreint que
    # `ProductRead` (pas de is_featured/is_published/dates internes) : on
    # vérifie que ces champs ne sont pas exposés publiquement.
    collection = collection_factory(is_published=True)
    product_factory(collection_id=collection.id, is_published=True)

    body = client.get("/products").json()[0]

    assert "is_featured" not in body
    assert "is_published" not in body
    assert "created_at" not in body


def test_public_product_embeds_its_variants_with_computed_price(
    client, collection_factory, product_factory, variant_factory
):
    collection = collection_factory(is_published=True)
    product = product_factory(collection_id=collection.id, price=19.99)
    variant_factory(product_id=product.id, sku="SKU-BASE", size="M")
    variant_factory(product_id=product.id, sku="SKU-PROMO", size="L", price_override=9.99)

    body = client.get("/products").json()[0]

    # `PublicVariantRead` n'expose pas le sku (voir le schéma) : on
    # distingue donc les variantes par leur taille.
    variants_by_size = {v["size"]: v["price"] for v in body["variants"]}
    assert variants_by_size == {"M": 19.99, "L": 9.99}
    assert "sku" not in body["variants"][0]


def test_get_public_product_returns_a_published_product(client, collection_factory, product_factory):
    collection = collection_factory(is_published=True)
    product = product_factory(collection_id=collection.id, name="Veste", is_published=True)

    response = client.get(f"/products/{product.id}")

    assert response.status_code == 200
    assert response.json()["name"] == "Veste"


def test_get_public_product_returns_404_for_an_unpublished_product(
    client, collection_factory, product_factory
):
    collection = collection_factory(is_published=True)
    product = product_factory(collection_id=collection.id, is_published=False)

    response = client.get(f"/products/{product.id}")

    assert response.status_code == 404


def test_get_public_product_returns_404_when_the_collection_is_unpublished(
    client, collection_factory, product_factory
):
    collection = collection_factory(is_published=False)
    product = product_factory(collection_id=collection.id, is_published=True)

    response = client.get(f"/products/{product.id}")

    assert response.status_code == 404


def test_get_public_product_returns_404_when_missing(client):
    response = client.get("/products/999")

    assert response.status_code == 404
