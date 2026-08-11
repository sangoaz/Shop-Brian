from fastapi import HTTPException
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

from app.models.collections import Collection
from app.models.product import Product
from app.utils.collections import get_collection_or_404

def get_product_or_404(session: Session, collection_id: int, product_id: int) -> Product:

    # On vérifie d'abord si la collection existe
    existing_collection = get_collection_or_404(session, collection_id)

    product = session.exec(
        select(Product).where(
            Product.id == product_id,
            Product.collection_id == collection_id,
        )
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Produit introuvable")

    return product

def visible_product_statement():
    return (
        select(Product)
        .options(selectinload(Product.variants))
        .join(Collection, Product.collection_id == Collection.id)
        .where(
            Product.is_published == True,
            Collection.is_published == True,
        )
    )



