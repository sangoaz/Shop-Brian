from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.address import Address


def get_address_or_404(session: Session, user_id: int, address_id: int) -> Address:
    address = session.exec(
        select(Address).where(
            Address.id == address_id,
            Address.user_id == user_id,
        )
    ).first()

    if not address:
        raise HTTPException(status_code=404, detail="Adresse introuvable")

    return address


def clear_existing_default(session: Session, user_id: int, field: str) -> None:
    """Désactive l'ancien défaut (shipping ou billing) du client avant d'en activer un nouveau."""
    statement = select(Address).where(
        Address.user_id == user_id,
        getattr(Address, field) == True,
    )
    for address in session.exec(statement).all():
        setattr(address, field, False)
        session.add(address)