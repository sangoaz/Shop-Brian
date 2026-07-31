from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.collections import Collection
from app.models.product import Product
from app.utils.collections import get_collection_or_404

def get_product_or_404(session: Session, collection_id: int, clothing_id: int) -> Clothing:

    # On vérifie d'abord si la collection existe
    existing_collection = get_collection_or_404(session, collection_id)

    clothing = session.exec(
        select(Clothing).where(
            Clothing.id == clothing_id,
            Clothing.collection_id == collection_id,
        )
    ).first()

    if not clothing:
        raise HTTPException(status_code=404, detail="Vetement introuvable")

    return clothing

def visible_clothing_statement():

    return (
        select(Clothing)
        .join(Collection, Clothing.collection_id == Collection.id)
        .where(
            Clothing.is_published == True,
            Collection.is_published == True,
        )
    )

