from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.product import Product
from app.models.product_variant import ProductVariant

from app.utils.product import get_product_or_404

def get_variant_or_404(session: Session, collection_id: int, product_id: int, variant_id: int) -> ProductVariant:

    # On vérifie si le produit existe
    existing_product = get_product_or_404(session, collection_id, product_id)

    variant = session.exec(
        select(ProductVariant).where(
            ProductVariant.id == variant_id,
            ProductVariant.product_id == product_id,
        )
    ).first()

    if not variant:
        raise HTTPException(status_code=404, detail="Variation du produit introuvable")
    
    return variant

