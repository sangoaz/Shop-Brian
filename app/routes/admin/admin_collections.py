""" Routes relatives aux collections """

from datetime import datetime, timezone
from fastapi import APIRouter, Query, Depends
from sqlmodel import select, Session
from typing import List

from app.core.database import get_session
from app.deps.auth import require_admin
from app.models.collections import Collection
from app.models.user import User
from app.schemas.collections import(
    CollectionCreate,
    CollectionUpdate,
    CollectionRead,
)
from app.utils.collections import get_collection_or_404


router = APIRouter(prefix="/admin", tags=["Collections"])

# ====================
# Collections
# ====================

# Enregistrer une nouvelle collection
@router.post("/collections", status_code=201, response_model=CollectionRead)
def create_collection(
    collection: CollectionCreate,
    session: Session = Depends(get_session),
    admin_user: User = Depends(require_admin),
):
    new_collection = Collection(**collection.model_dump())

    session.add(new_collection)
    session.commit()
    session.refresh(new_collection)

    return new_collection

# Liste des collections
@router.get("/collections", response_model=List[CollectionRead])
def list_collection(
    admin_user: User = Depends(require_admin),
    session: Session = Depends(get_session),
    limit: int = Query(default=20, le=20),
    offset: int = Query(default=0, ge=0),
):
    
    statement = (
        select(Collection).order_by(Collection.created_at.desc()).offset(offset).limit(limit)
    )

    collections = session.exec(statement).all()

    return collections

# Afficher une collection
@router.get("/collections/{collection_id}", response_model=CollectionRead)
def get_collection(
    collection_id: int,
    admin_user: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    
    collection = get_collection_or_404(session, collection_id)

    return collection

# Mise à jour d'un collection
@router.patch("/collections/{collection_id}", response_model=CollectionRead)
def update_collection(
    collection_id: int,
    collection: CollectionUpdate,
    admin_user: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    
    existing_collection = get_collection_or_404(session, collection_id)

    updated_data = collection.model_dump(exclude_unset=True)

    for field, value in updated_data.items():
        setattr(existing_collection, field, value)

    existing_collection.updated_at = datetime.now(timezone.utc)

    session.commit()
    session.refresh(existing_collection)

    return existing_collection

