"""
Tests des modèles SQLModel (app/models/user.py, product.py, product_variant.py,
collections.py).

Depuis le refactor Clothing -> Product, le catalogue est en deux niveaux :
un `Product` décrit les informations communes (nom, catégorie, prix de
base, description), et chacune de ses `ProductVariant` porte la taille, le
stock, le SKU et un éventuel prix de substitution (`price_override`).

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
from app.models.collections import Collection, CollectionImage
from app.models.product import Product, ProductImage
from app.models.product_variant import ProductVariant
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


class TestProductDefaults:
    def test_visibility_flags_default_values(self):
        product = Product(
            name="Pull",
            item=Item.SWEATS,
            price=39.90,
            description="Pull chaud",
            collection_id=1,
        )
        assert product.is_featured is True
        assert product.is_published is True

    def test_product_no_longer_carries_size_or_stock(self):
        # Régression : `size` et `stock` ont été déplacés vers
        # `ProductVariant` lors du refactor. Ce test documente qu'un
        # `Product` ne les expose plus du tout (plutôt qu'un test qui
        # échouerait silencieusement si on les réintroduisait par erreur).
        product = Product(
            name="Pull",
            item=Item.SWEATS,
            price=39.90,
            description="Pull chaud",
            collection_id=1,
        )
        assert not hasattr(product, "size")
        assert not hasattr(product, "stock")


class TestProductVariantDefaults:
    def test_is_expired_defaults_to_false(self):
        variant = ProductVariant(size=Size.M, stock=5, sku="SKU-1", product_id=1)
        assert variant.is_expired is False

    def test_price_override_defaults_to_none(self):
        variant = ProductVariant(size=Size.M, stock=5, sku="SKU-1", product_id=1)
        assert variant.price_override is None

    def test_effective_price_uses_override_when_set(self, session, collection_factory, product_factory):
        collection = collection_factory()
        product = product_factory(collection_id=collection.id, price=19.99)
        variant = ProductVariant(
            size=Size.M, stock=5, sku="SKU-OVERRIDE", product_id=product.id, price_override=9.99
        )
        session.add(variant)
        session.commit()
        session.refresh(variant)

        assert variant.effective_price == 9.99

    def test_effective_price_falls_back_to_product_price_when_no_override(
        self, session, collection_factory, product_factory
    ):
        collection = collection_factory()
        product = product_factory(collection_id=collection.id, price=19.99)
        variant = ProductVariant(size=Size.M, stock=5, sku="SKU-NO-OVERRIDE", product_id=product.id)
        session.add(variant)
        session.commit()
        session.refresh(variant)

        assert variant.effective_price == 19.99


class TestCollectionProductRelationship:
    """
    Ces tests persistent réellement les objets en base pour vérifier que les
    relations bidirectionnelles déclarées via `Relationship(back_populates=...)`
    fonctionnent, y compris après un rechargement depuis la base (`refresh`).
    """

    def test_product_exposes_its_collection(self, session, collection_factory, product_factory):
        collection = collection_factory(name="Printemps 2026")
        product = product_factory(collection_id=collection.id, name="Short")

        session.refresh(product)

        assert product.collection.id == collection.id
        assert product.collection.name == "Printemps 2026"

    def test_collection_lists_all_its_products(self, session, collection_factory, product_factory):
        collection = collection_factory()
        product_factory(collection_id=collection.id, name="T-shirt")
        product_factory(collection_id=collection.id, name="Short")

        session.refresh(collection)

        names = {item.name for item in collection.products}
        assert names == {"T-shirt", "Short"}

    def test_collection_without_products_has_empty_list(self, session, collection_factory):
        collection = collection_factory()
        session.refresh(collection)

        assert collection.products == []


class TestProductVariantRelationship:
    def test_product_lists_all_its_variants(
        self, session, collection_factory, product_factory, variant_factory
    ):
        collection = collection_factory()
        product = product_factory(collection_id=collection.id)
        variant_factory(product_id=product.id, sku="SKU-A")
        variant_factory(product_id=product.id, sku="SKU-B")

        session.refresh(product)

        skus = {variant.sku for variant in product.variants}
        assert skus == {"SKU-A", "SKU-B"}

    def test_variant_exposes_its_product(
        self, session, collection_factory, product_factory, variant_factory
    ):
        collection = collection_factory()
        product = product_factory(collection_id=collection.id, name="Veste")
        variant = variant_factory(product_id=product.id)

        session.refresh(variant)

        assert variant.product.id == product.id
        assert variant.product.name == "Veste"

    def test_product_without_variants_has_empty_list(self, session, collection_factory, product_factory):
        collection = collection_factory()
        product = product_factory(collection_id=collection.id)
        session.refresh(product)

        assert product.variants == []


class TestImageModels:
    def test_product_image_links_back_to_its_product(
        self, session, collection_factory, product_factory
    ):
        collection = collection_factory()
        product = product_factory(collection_id=collection.id)

        image = ProductImage(product_id=product.id, image_url="https://example.com/a.jpg")
        session.add(image)
        session.commit()
        session.refresh(image)

        assert image.product.id == product.id
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
