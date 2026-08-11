""" Routes publiques relatives aux produits"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import select, Session

from app.core.database import get_session
from app.models.product import Product
from app.schemas.product import PublicProductRead
from app.utils.product import visible_product_statement

router = APIRouter(prefix="/collections", tags=["Public Products in collection"])


# Liste des produits d'une collection
@router.get("/{collection_id}/products", response_model=list[PublicProductRead])
def list_public_products_in_collection(
    collection_id: int,
    session: Session = Depends(get_session),
    limit: int = Query(default=20, le=20),
    offset: int = Query(default=0, ge=0),
):
    statement = (
        visible_product_statement()
        .where(Product.collection_id == collection_id)
        .order_by(Product.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    products = session.exec(statement).all()
    return products


# Afficher un seul produit
@router.get("/{collection_id}/product/{product_id}", response_model=PublicProductRead)
def get_public_product_in_collection(
    collection_id: int,
    product_id: int,
    session: Session = Depends(get_session),
):
    statement = visible_product_statement().where(
        Product.id == product_id,
        Product.collection_id == collection_id,
    )
    product = session.exec(statement).first()

    if not product:
        raise HTTPException(status_code=404, detail="Vetement introuvable")

    return product