""" Routes relatives aux vetements """

from datetime import datetime, timezone
from fastapi import APIRouter, Query, Depends, Form
from sqlmodel import select, Session
from typing import List

from app.core.database import get_session
from app.deps.auth import get_current_user, require_admin
from app.models.clothes import Clothing
from app.models.user import User
from app.schemas.clothes import(
    ClothingCreate,
    ClothingRead,
    ClothingUpdate,
)
from app.utils.clothes import get_clothing_or_404
from app.utils.collections import get_collection_or_404


router = APIRouter(prefix="/admin", tags=["Clothes"])

# ====================
# Clothes
# ====================

# Enregistrer un nouveau vetement
@router.post("/collections/{collection_id}/clothing", status_code=201, response_model=ClothingRead)
def create_clothing(
    collection_id: int,
    clothing: ClothingCreate,
    session: Session = Depends(get_session),
    admin_user: User = Depends(require_admin),
):
    
    existing_collection = get_collection_or_404(session, collection_id)

    new_clothing = Clothing(**clothing.model_dump(), collection_id=collection_id)

    session.add(new_clothing)
    session.commit()
    session.refresh(new_clothing)

    return new_clothing


# Liste des vetements
@router.get("/collections/{collection_id}/clothes", response_model=List[ClothingRead])
def list_clothes(
    collection_id: int,
    admin_user: User = Depends(require_admin),
    session: Session = Depends(get_session),
    limit: int = Query(default=20, le=20),
    offset: int = Query(default=0, ge=0),
):
    
    existing_collection = get_collection_or_404(session, collection_id)

    statement = (
        select(Clothing).order_by(Clothing.created_at.desc()).offset(offset).limit(limit).where(Clothing.collection_id == collection_id)
    )

    clothing = session.exec(statement).all()

    return clothing


# Afficher un vetement
@router.get("/collections/{collection_id}/clothing/{clothing_id}", response_model=ClothingRead)
def get_cothing(
    collection_id: int,
    clothing_id: int,
    admin_user: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    
    clothing = get_clothing_or_404(session, collection_id, clothing_id)

    return clothing


# Mise à jour d'un vetement
@router.patch("/collections/{collection_id}/clothing/{clothing_id}", response_model=ClothingRead)
def update_clothing(
    collection_id: int,
    clothing_id: int,
    clothing: ClothingUpdate,
    admin_user: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    
    existing_clothing = get_clothing_or_404(session, collection_id, clothing_id)

    updated_data = clothing.model_dump(exclude_unset=True)

    for field, value in updated_data.items():
        setattr(existing_clothing, field, value)

    existing_clothing.updated_at = datetime.now(timezone.utc)

    session.commit()
    session.refresh(existing_clothing)

    return existing_clothing

