"""
Script de seed : remplit la db avec des données factices (2 collections,
3-4 produits par collection, quelques variantes par produit) pour tester
rapidement sans passer par les routes de l'API.

Usage :
    python seed_db.py

Idempotent : si une collection du même nom existe déjà, elle est ignorée.
"""

from sqlmodel import Session, select

from app.core.database import engine
import app.models  # force l'import de tous les modèles (voir app/models/__init__.py)
from app.models.collections import Collection
from app.models.product import Product
from app.models.product_variant import ProductVariant
from app.enums import Item, Size


SEED_DATA = [
    {
        "collection": {"name": "Collection Été 2026", "is_published": True},
        "products": [
            {
                "name": "T-shirt Oversize Blanc",
                "item": Item.T_SHIRT,
                "price": 29.90,
                "description": "T-shirt oversize 100% coton, coupe décontractée.",
                "sizes": [Size.S, Size.M, Size.L],
            },
            {
                "name": "Short Cargo Kaki",
                "item": Item.SHORTS,
                "price": 39.90,
                "description": "Short cargo multipoches, tissu résistant.",
                "sizes": [Size.M, Size.L, Size.XL],
            },
            {
                "name": "Casquette Logo",
                "item": Item.ACCESSORIES,
                "price": 19.90,
                "description": "Casquette brodée, taille unique ajustable.",
                "sizes": [Size.XS],
            },
            {
                "name": "Boxer Pack x3",
                "item": Item.UNDERWEAR,
                "price": 24.90,
                "description": "Lot de 3 boxers en coton stretch.",
                "sizes": [Size.S, Size.M, Size.L],
            },
        ],
    },
    {
        "collection": {"name": "Collection Hiver 2026", "is_published": True},
        "products": [
            {
                "name": "Sweat à Capuche Gris",
                "item": Item.SWEATS,
                "price": 49.90,
                "description": "Sweat à capuche molletonné, poche kangourou.",
                "sizes": [Size.S, Size.M, Size.L, Size.XL],
            },
            {
                "name": "Veste Doudoune Noire",
                "item": Item.JACKETS,
                "price": 89.90,
                "description": "Doudoune légère et chaude, déperlante.",
                "sizes": [Size.M, Size.L, Size.XL],
            },
            {
                "name": "Pantalon Jogger Noir",
                "item": Item.PANTS,
                "price": 44.90,
                "description": "Jogger en molleton, chevilles resserrées.",
                "sizes": [Size.S, Size.M, Size.L],
            },
        ],
    },
]


def seed() -> None:
    with Session(engine) as session:
        sku_counter = 1

        for entry in SEED_DATA:
            collection_data = entry["collection"]

            existing = session.exec(
                select(Collection).where(Collection.name == collection_data["name"])
            ).first()

            if existing:
                print(f"Collection déjà en db, ignorée : {collection_data['name']}")
                continue

            collection = Collection(**collection_data)
            session.add(collection)
            session.commit()
            session.refresh(collection)
            print(f"Collection créée : {collection.name} (id={collection.id})")

            for product_data in entry["products"]:
                sizes = product_data.pop("sizes")

                product = Product(
                    collection_id=collection.id,
                    **product_data,
                )
                session.add(product)
                session.commit()
                session.refresh(product)
                print(f"  Produit créé : {product.name} (id={product.id})")

                for size in sizes:
                    variant = ProductVariant(
                        size=size,
                        stock=20,
                        sku=f"SEED-{sku_counter:04d}",
                        product_id=product.id,
                    )
                    session.add(variant)
                    sku_counter += 1

                session.commit()
                print(f"    {len(sizes)} variante(s) créée(s)")

    print("Seed terminé.")


if __name__ == "__main__":
    seed()
