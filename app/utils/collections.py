from fastapi import HTTPException
from sqlmodel import Session

from app.models.collections import Collection


def get_collection_or_404(session: Session, collection_id: int) -> Collection:
    collection = session.get(Collection, collection_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection introuvable")
    return collection