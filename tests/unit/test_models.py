"""
Tests des modèles SQLModel (app/models/user.py, clothes.py, collections.py).

Deux catégories de tests ici :

- les tests de "valeurs par défaut" instancient un modèle sans le persister :
  ils vérifient uniquement le comportement Python de la classe (utile,
  rapide, pas besoin de base de données) ;
- les tests de "relations" persistent réellement les objets via la fixture
  `session` (SQLite en mémoire) car une relation SQLModel (`Relationship`)
  n'est peuplée qu'après un aller-retour en base.
"""

from datetime import datetime, timezone

import pytest

from app.enums import Item, Size, UserRole
from app.models.product_variant import Clothing, ClothingImage
from app.models.collections import Collection, CollectionImage
from app.models.user import User

pytestmark = pytest.mark.unit


class TestUserDefaults:
    def test_role_defaults_to_admin(self):
        user = User(email="a@example.com", password_hash="hashed")
        assert user.role == UserRole.ADMIN

    def test_is_active_defaults_to_true(self):
        user = User(email="a@example.com", password_hash="hashed")
        assert user.is_active is True

    def test_created_at_defaults_to_a_timezone_aware_now(self):
        before = datetime.now(timezone.utc)
        user = User(email="a@example.com", password_hash="hashed")
        after = datetime.now(timezone.utc)

        assert user.created_at.tzinfo is not None
        assert before <= user.created_at <= after


class TestCollectionDefaults:
    def test_is_published_defaults_to_true(self):
        collection = Collection(name="Hiver 2026")
        assert collection.is_published is True

    def test_end_has_no_default(self):
        collection = Collection(name="Hiver 2026")
        assert collection.end is None

    def test_start_defaults_to_now(self):
        before = datetime.now(timezone.utc)
        collection = Collection(name="Hiver 2026")
        after = datetime.now(timezone.utc)

        assert before <= collection.start <= after


class TestClothingDefaults:
    def test_visibility_flags_default_values(self):
        clothing = Clothing(
            name="Pull",
            item=Item.SWEATS,
            size=Size.L,
            price=39.90,
            description="Pull chaud",
            stock=5,
            collection_id=1,
        )
        assert clothing.is_featured is True
        assert clothing.is_published is True
        assert clothing.is_expired is False


class TestCollectionClothingRelationship:
    """
    Ces tests persistent réellement les objets en base pour vérifier que les
    relations bidirectionnelles déclarées via `Relationship(back_populates=...)`
    fonctionnent, y compris après un rechargement depuis la base (`refresh`).
    """

    def test_clothing_exposes_its_collection(self, session, collection_factory, clothing_factory):
        collection = collection_factory(name="Printemps 2026")
        clothing = clothing_factory(collection_id=collection.id, name="Short")

        session.refresh(clothing)

        assert clothing.collection.id == collection.id
        assert clothing.collection.name == "Printemps 2026"

    def test_collection_lists_all_its_clothes(self, session, collection_factory, clothing_factory):
        collection = collection_factory()
        clothing_factory(collection_id=collection.id, name="T-shirt")
        clothing_factory(collection_id=collection.id, name="Short")

        session.refresh(collection)

        names = {item.name for item in collection.clothes}
        assert names == {"T-shirt", "Short"}

    def test_collection_without_clothes_has_empty_list(self, session, collection_factory):
        collection = collection_factory()
        session.refresh(collection)

        assert collection.clothes == []


class TestImageModels:
    def test_clothing_image_links_back_to_its_clothing(
        self, session, collection_factory, clothing_factory
    ):
        collection = collection_factory()
        clothing = clothing_factory(collection_id=collection.id)

        image = ClothingImage(clothing_id=clothing.id, image_url="https://example.com/a.jpg")
        session.add(image)
        session.commit()
        session.refresh(image)

        assert image.clothing.id == clothing.id
        # display_order / is_cover ont des valeurs par défaut exploitées par
        # le tri d'affichage côté front : on les fige ici.
        assert image.is_cover is True
        assert image.display_order == 0

    def test_collection_image_links_back_to_its_collection(self, session, collection_factory):
        collection = collection_factory()

        image = CollectionImage(collection_id=collection.id, image_url="https://example.com/b.jpg")
        session.add(image)
        session.commit()
        session.refresh(image)

        assert image.collection.id == collection.id
