"""
Tests d'intégration de app/routes/public/public_clothes_in_collection.py.

Ce module expose deux routes sous /collections/{collection_id}/... :
la liste des vêtements visibles d'une collection, et le détail d'un
vêtement. Comme pour les autres routes publiques, un vêtement non publié
(ou rattaché à une collection non publiée) doit rester invisible.
"""

import pytest

pytestmark = pytest.mark.integration


class TestListClothesInCollection:
    def test_does_not_require_authentication(self, client, collection_factory):
        collection = collection_factory(is_published=True)

        response = client.get(f"/collections/{collection.id}/clothes")

        assert response.status_code == 200

    def test_only_returns_published_clothing(self, client, collection_factory, clothing_factory):
        collection = collection_factory(is_published=True)
        clothing_factory(collection_id=collection.id, name="Visible", is_published=True)
        clothing_factory(collection_id=collection.id, name="Brouillon", is_published=False)

        response = client.get(f"/collections/{collection.id}/clothes")

        names = [item["name"] for item in response.json()]
        assert names == ["Visible"]

    def test_returns_nothing_for_an_unpublished_collection(
        self, client, collection_factory, clothing_factory
    ):
        collection = collection_factory(is_published=False)
        clothing_factory(collection_id=collection.id, name="Caché", is_published=True)

        response = client.get(f"/collections/{collection.id}/clothes")

        # Pas de 404 ici : la route liste simplement les vêtements visibles
        # de la collection, sans vérifier au préalable que la collection
        # elle-même existe ou est publiée. Une collection non publiée se
        # traduit donc par une liste vide plutôt qu'une erreur.
        assert response.status_code == 200
        assert response.json() == []

    def test_only_returns_clothes_from_the_requested_collection(
        self, client, collection_factory, clothing_factory
    ):
        collection_a = collection_factory(is_published=True)
        collection_b = collection_factory(is_published=True)
        clothing_factory(collection_id=collection_a.id, name="Dans A")
        clothing_factory(collection_id=collection_b.id, name="Dans B")

        response = client.get(f"/collections/{collection_a.id}/clothes")

        names = [item["name"] for item in response.json()]
        assert names == ["Dans A"]


class TestGetSingleClothing:
    def test_returns_the_matching_clothing(self, client, collection_factory, clothing_factory):
        collection = collection_factory(is_published=True)
        clothing = clothing_factory(collection_id=collection.id, name="Veste", is_published=True)

        response = client.get(f"/collections/{collection.id}/clothing/{clothing.id}")

        assert response.status_code == 200
        assert response.json()["name"] == "Veste"

    def test_returns_404_for_unpublished_clothing(self, client, collection_factory, clothing_factory):
        collection = collection_factory(is_published=True)
        clothing = clothing_factory(collection_id=collection.id, is_published=False)

        response = client.get(f"/collections/{collection.id}/clothing/{clothing.id}")

        assert response.status_code == 404

    def test_returns_404_when_the_collection_is_unpublished(
        self, client, collection_factory, clothing_factory
    ):
        collection = collection_factory(is_published=False)
        clothing = clothing_factory(collection_id=collection.id, is_published=True)

        response = client.get(f"/collections/{collection.id}/clothing/{clothing.id}")

        assert response.status_code == 404

    def test_returns_404_when_missing(self, client, collection_factory):
        collection = collection_factory(is_published=True)

        response = client.get(f"/collections/{collection.id}/clothing/999")

        assert response.status_code == 404

    def test_returns_404_for_the_wrong_collection(
        self, client, collection_factory, clothing_factory
    ):
        collection_a = collection_factory(is_published=True)
        collection_b = collection_factory(is_published=True)
        clothing = clothing_factory(collection_id=collection_a.id, is_published=True)

        response = client.get(f"/collections/{collection_b.id}/clothing/{clothing.id}")

        assert response.status_code == 404
