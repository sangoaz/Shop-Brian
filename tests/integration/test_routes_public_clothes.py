"""
Tests d'intégration de app/routes/public/public_clothes.py (GET /clothes/).

Cette route liste tous les vêtements, toutes collections confondues, en ne
montrant que ceux qui sont à la fois publiés eux-mêmes ET rattachés à une
collection publiée (voir `visible_clothing_statement` dans
app/utils/clothes.py, testée aussi côté unitaire dans
tests/unit/test_utils_clothes.py).
"""

import pytest

pytestmark = pytest.mark.integration


def test_list_public_clothes_does_not_require_authentication(client):
    response = client.get("/clothes/")

    assert response.status_code == 200


def test_list_public_clothes_excludes_unpublished_clothing(
    client, collection_factory, clothing_factory
):
    collection = collection_factory(is_published=True)
    clothing_factory(collection_id=collection.id, name="En vente", is_published=True)
    clothing_factory(collection_id=collection.id, name="Brouillon", is_published=False)

    response = client.get("/clothes/")

    names = [item["name"] for item in response.json()]
    assert names == ["En vente"]


def test_list_public_clothes_excludes_clothing_from_an_unpublished_collection(
    client, collection_factory, clothing_factory
):
    published_collection = collection_factory(is_published=True)
    draft_collection = collection_factory(is_published=False)
    clothing_factory(collection_id=published_collection.id, name="Visible")
    clothing_factory(collection_id=draft_collection.id, name="Caché", is_published=True)

    response = client.get("/clothes/")

    names = [item["name"] for item in response.json()]
    assert names == ["Visible"]


def test_public_clothing_read_does_not_expose_stock(client, collection_factory, clothing_factory):
    # `PublicClothingRead` est volontairement plus restreint que
    # `ClothingRead` (pas de stock, pas de dates internes) : on vérifie que
    # ces champs ne sont pas exposés publiquement.
    collection = collection_factory(is_published=True)
    clothing_factory(collection_id=collection.id, stock=42)

    response = client.get("/clothes/")

    body = response.json()[0]
    assert "stock" not in body


def test_list_public_clothes_limit_is_capped_at_20(client):
    response = client.get("/clothes/?limit=21")

    assert response.status_code == 422
