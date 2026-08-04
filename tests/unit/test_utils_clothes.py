"""
Tests de app/utils/clothes.py.

`get_product_or_404` vérifie deux choses en cascade : que la collection
existe, puis que le produit existe ET appartient bien à cette collection.
Chaque cas d'échec est testé séparément pour documenter précisément quelle
condition déclenche le 404.

`visible_product_statement` construit la requête utilisée par les routes
publiques (app/routes/public/*.py) : un produit n'est "visible" que s'il
est lui-même publié ET rattaché à une collection publiée. On teste cette
fonction directement ici (en exécutant la requête qu'elle produit) plutôt
que seulement via les routes publiques, pour isoler la logique de
filtrage de la sérialisation HTTP.
"""

import pytest
from fastapi import HTTPException

from app.utils.product import get_product_or_404, visible_product_statement

pytestmark = pytest.mark.unit


def test_returns_the_matching_product(session, collection_factory, product_factory):
    collection = collection_factory()
    product = product_factory(collection_id=collection.id, name="Veste")

    result = get_product_or_404(session, collection.id, product.id)

    assert result.id == product.id
    assert result.name == "Veste"


def test_raises_404_when_the_collection_does_not_exist(session):
    with pytest.raises(HTTPException) as exc_info:
        get_product_or_404(session, collection_id=999, product_id=1)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Collection introuvable"


def test_raises_404_when_the_product_does_not_exist(session, collection_factory):
    collection = collection_factory()

    with pytest.raises(HTTPException) as exc_info:
        get_product_or_404(session, collection.id, product_id=999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Vetement introuvable"


def test_raises_404_when_the_product_belongs_to_another_collection(
    session, collection_factory, product_factory
):
    collection_a = collection_factory(name="Collection A")
    collection_b = collection_factory(name="Collection B")
    product_in_a = product_factory(collection_id=collection_a.id)

    # Le vêtement existe bel et bien, mais pas sous collection_b : il ne
    # doit pas être trouvable via cette URL-là.
    with pytest.raises(HTTPException) as exc_info:
        get_product_or_404(session, collection_b.id, product_in_a.id)

    assert exc_info.value.status_code == 404


class TestVisibleProductStatement:
    def test_includes_published_product_in_a_published_collection(
        self, session, collection_factory, product_factory
    ):
        collection = collection_factory(is_published=True)
        product_factory(collection_id=collection.id, name="Visible", is_published=True)

        results = session.exec(visible_product_statement()).all()

        assert [item.name for item in results] == ["Visible"]

    def test_excludes_unpublished_product(self, session, collection_factory, product_factory):
        collection = collection_factory(is_published=True)
        product_factory(collection_id=collection.id, is_published=False)

        results = session.exec(visible_product_statement()).all()

        assert results == []

    def test_excludes_product_from_an_unpublished_collection(
        self, session, collection_factory, product_factory
    ):
        collection = collection_factory(is_published=False)
        product_factory(collection_id=collection.id, is_published=True)

        results = session.exec(visible_product_statement()).all()

        assert results == []
