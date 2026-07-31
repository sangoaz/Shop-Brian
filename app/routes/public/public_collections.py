""" Routes relatives au collections """

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import select, Session

from app.core.database import get_session
from app.models.collections import Collection
from app.schemas.collections import PublicCollectionRead

router = APIRouter(prefix="/collections", tags=["Public Collections"])


# Liste des collections
@router.get("", response_model=list[PublicCollectionRead])
def list_public_collections(
    session: Session = Depends(get_session),
    limit: int = Query(default=20, le=20),
    offset: int = Query(default=0, ge=0),
):
    statement = (
        select(Collection)
        .where(Collection.is_published == True)
        .order_by(Collection.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    collections = session.exec(statement).all()
    return collections


# Afficher une seule collection
@router.get("/{collection_id}", response_model=PublicCollectionRead)
def get_public_collection(
    collection_id: int,
    session: Session = Depends(get_session),
):
    statement = select(Collection).where(
        Collection.id == collection_id,
        Collection.is_published == True,
    )

    collection = session.exec(statement).first()

    if not collection:
        raise HTTPException(status_code=404, detail="Collection introuvable")

    return collection