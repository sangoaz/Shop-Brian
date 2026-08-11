from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import select, Session

from app.core.database import get_session
from app.models.product import Product
from app.schemas.product import PublicProductRead
from app.utils.product import visible_product_statement

router = APIRouter(prefix="/products", tags=["Public Products"])


# Liste de tous les produits
@router.get("", response_model=list[PublicProductRead])
def list_public_products(
    collection_id: int | None = None,
    session: Session = Depends(get_session),
    limit: int = Query(default=20, le=20),
    offset: int = Query(default=0, ge=0),
):
    
    statement = visible_product_statement()

    if collection_id is not None:
        statement = statement.where(Product.collection_id == collection_id)

    statement = statement.order_by(Product.created_at.desc()).offset(offset).limit(limit)
    
    products = session.exec(statement).all()
    return products

# Afficher un seul produit
@router.get("/{product_id}", response_model=PublicProductRead)
def get_public_product(
    product_id: int,
    session: Session = Depends(get_session),
):
    statement = visible_product_statement().where(
        Product.id == product_id
    )

    product = session.exec(statement).first()

    if not product:
        raise HTTPException(status_code=404, detail="Produit introuvable")
    
    return product