""" Routes relatives aux produits """

from datetime import datetime, timezone
from fastapi import APIRouter, Query, Depends
from sqlmodel import select, Session
from typing import List

from app.core.database import get_session
from app.deps.auth import require_admin
from app.models.product import Product
from app.models.user import User
from app.schemas.product import(
    ProductCreate,
    ProductRead,
    ProductUpdate,
)
from app.utils.product import get_product_or_404
from app.utils.collections import get_collection_or_404


router = APIRouter(prefix="/admin", tags=["Products"])

# ====================
# Product
# ====================

# Enregistrer un nouveau produit
@router.post("/collections/{collection_id}/product", status_code=201, response_model=ProductRead)
def create_product(
    collection_id: int,
    product: ProductCreate,
    session: Session = Depends(get_session),
    admin_user: User = Depends(require_admin),
):
    
    existing_collection = get_collection_or_404(session, collection_id)

    new_product = Product(**product.model_dump(), collection_id=collection_id)

    session.add(new_product)
    session.commit()
    session.refresh(new_product)

    return new_product


# Liste des produits
@router.get("/collections/{collection_id}/products", response_model=List[ProductRead])
def list_products(
    collection_id: int,
    admin_user: User = Depends(require_admin),
    session: Session = Depends(get_session),
    limit: int = Query(default=20, le=20),
    offset: int = Query(default=0, ge=0),
):
    
    existing_collection = get_collection_or_404(session, collection_id)

    statement = (
        select(Product).order_by(Product.created_at.desc()).offset(offset).limit(limit).where(Product.collection_id == collection_id)
    )

    product = session.exec(statement).all()

    return product


# Afficher un produit
@router.get("/collections/{collection_id}/product/{product_id}", response_model=ProductRead)
def get_product(
    collection_id: int,
    product_id: int,
    admin_user: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    
    product = get_product_or_404(session, collection_id, product_id)

    return product


# Mise à jour d'un produit
@router.patch("/collections/{collection_id}/product/{product_id}", response_model=ProductRead)
def update_product(
    collection_id: int,
    product_id: int,
    product: ProductUpdate,
    admin_user: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    
    existing_product = get_product_or_404(session, collection_id, product_id)

    updated_data = product.model_dump(exclude_unset=True)

    for field, value in updated_data.items():
        setattr(existing_product, field, value)

    existing_product.updated_at = datetime.now(timezone.utc)

    session.commit()
    session.refresh(existing_product)

    return existing_product

