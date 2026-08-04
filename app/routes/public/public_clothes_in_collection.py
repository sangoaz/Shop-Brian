""" Routes publiques relatives aux vêtements des collections"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import select, Session

from app.core.database import get_session
from app.models.product import Product
from app.schemas.product import PublicClothingRead
from app.utils.clothes import visible_clothing_statement

router = APIRouter(prefix="/collections", tags=["Public Clothes in collection"])


# Liste des vêtements d'une collection
@router.get("/{collection_id}/clothes", response_model=list[PublicClothingRead])
def list_public_clothes_in_collection(
    collection_id: int,
    session: Session = Depends(get_session),
    limit: int = Query(default=20, le=20),
    offset: int = Query(default=0, ge=0),
):
    statement = (
        visible_clothing_statement()
        .where(Clothing.collection_id == collection_id)
        .order_by(Clothing.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    clothes = session.exec(statement).all()
    return clothes


# Afficher un seul vetement
@router.get("/{collection_id}/clothing/{clothing_id}", response_model=PublicClothingRead)
def get_public_clothing(
    collection_id: int,
    clothing_id: int,
    session: Session = Depends(get_session),
):
    statement = visible_clothing_statement().where(
        Clothing.id == clothing_id,
        Clothing.collection_id == collection_id,
    )
    clothing = session.exec(statement).first()

    if not clothing:
        raise HTTPException(status_code=404, detail="Vetement introuvable")

    return clothing