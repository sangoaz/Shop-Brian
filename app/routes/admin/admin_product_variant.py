""" Routes relatives aux variantes de produits """

from datetime import datetime, timezone
from fastapi import APIRouter, Query, Depends
from sqlmodel import select, Session
from typing import List

from app.core.database import get_session
from app.deps.auth import require_admin
from app.models.product import Product
from app.models.product_variant import ProductVariant
from app.models.user import User
from app.schemas.product_variant import(
    VariantCreate,
    VariantRead,
    VariantUpdate,
)
from app.utils.product import get_product_or_404
from app.utils.product_variant import get_variant_or_404


router = APIRouter(prefix="/admin", tags=["Variants"])

# ====================
# Variants
# ====================

# Enregister une nouvelle variation
@router.post("/collections/{collection_id}/products/{product_id}/variants", status_code=201, response_model=VariantRead)
def create_variant(
    collection_id: int,
    product_id: int,
    variant: VariantCreate,
    session: Session = Depends(get_session),
    admin_user: User = Depends(require_admin),
):
    
    existing_product = get_product_or_404(session, collection_id, product_id)

    new_variant = ProductVariant(**variant.model_dump(), product_id=product_id)

    session.add(new_variant)
    session.commit()
    session.refresh(new_variant)

    return new_variant

# Liste des variations d'un produit
@router.get("/collections/{collection_id}/products/{product_id}/variants", response_model=List[VariantRead])
def list_variant(
    collection_id: int,
    product_id: int,
    admin_user: User = Depends(require_admin),
    session: Session = Depends(get_session),
    limit: int = Query(default=20, le=20),
    offset: int = Query(default=0, ge=0),
):
    
    existing_product = get_product_or_404(session, collection_id, product_id)

    statement = (
        select(ProductVariant)
        .order_by(ProductVariant.created_at.desc())
        .offset(offset)
        .limit(limit)
        .where(ProductVariant.product_id == product_id)
    )

    variant = session.exec(statement).all()

    return variant

# Afficher une variation
@router.get("/collections/{collection_id}/products/{product_id}/variants/{variant_id}", response_model=VariantRead)
def get_variant(
    collection_id: int,
    product_id: int,
    variant_id: int,
    admin_user: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    
    variant = get_variant_or_404(session, collection_id, product_id, variant_id)

    return variant


# Mise à jour d'une variation
@router.patch("/collections/{collection_id}/products/{product_id}/variants/{variant_id}", response_model=VariantRead)
def update_variant(
    collection_id: int,
    product_id: int,
    variant_id: int,
    variant: VariantUpdate,
    admin_user: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    existing_variant = get_variant_or_404(session, collection_id, product_id, variant_id)

    updated_data = variant.model_dump(exclude_unset=True)

    for field, value in updated_data.items():
        setattr(existing_variant, field, value)

    existing_variant.updated_at = datetime.now(timezone.utc)

    session.commit()
    session.refresh(existing_variant)

    return existing_variant