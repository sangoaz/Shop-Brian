"""
Tests de app/utils/product_variant.py.

`get_variant_or_404` s'appuie sur `get_product_or_404` (voir
tests/unit/test_utils_product.py) : la cascade de vérification est donc à
trois niveaux — collection, puis produit, puis variante. Chaque niveau de
404 est testé séparément pour documenter précisément quelle condition
déclenche l'erreur.
"""

import pytest
from fastapi import HTTPException

from app.utils.product_variant import get_variant_or_404

pytestmark = pytest.mark.unit


def test_returns_the_matching_variant(session, collection_factory, product_factory, variant_factory):
    collection = collection_factory()
    product = product_factory(collection_id=collection.id)
    variant = variant_factory(product_id=product.id, sku="SKU-1")

    result = get_variant_or_404(session, collection.id, product.id, variant.id)

    assert result.id == variant.id
    assert result.sku == "SKU-1"


def test_raises_404_when_the_collection_does_not_exist(session):
    with pytest.raises(HTTPException) as exc_info:
        get_variant_or_404(session, collection_id=999, product_id=1, variant_id=1)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Collection introuvable"


def test_raises_404_when_the_product_does_not_exist(session, collection_factory):
    collection = collection_factory()

    with pytest.raises(HTTPException) as exc_info:
        get_variant_or_404(session, collection.id, product_id=999, variant_id=1)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Produit introuvable"


def test_raises_404_when_the_variant_does_not_exist(session, collection_factory, product_factory):
    collection = collection_factory()
    product = product_factory(collection_id=collection.id)

    with pytest.raises(HTTPException) as exc_info:
        get_variant_or_404(session, collection.id, product.id, variant_id=999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Variation du produit introuvable"


def test_raises_404_when_the_variant_belongs_to_another_product(
    session, collection_factory, product_factory, variant_factory
):
    collection = collection_factory()
    product_a = product_factory(collection_id=collection.id, name="Produit A")
    product_b = product_factory(collection_id=collection.id, name="Produit B")
    variant_of_a = variant_factory(product_id=product_a.id, sku="SKU-A")

    # La variante existe bel et bien, mais pas sous product_b : elle ne doit
    # pas être trouvable via cette URL-là.
    with pytest.raises(HTTPException) as exc_info:
        get_variant_or_404(session, collection.id, product_b.id, variant_of_a.id)

    assert exc_info.value.status_code == 404
