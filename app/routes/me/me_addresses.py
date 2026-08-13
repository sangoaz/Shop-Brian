""" Routes relatives aux adresses du client connecté """

from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlmodel import select, Session
from typing import List

from app.core.database import get_session
from app.deps.auth import get_current_user
from app.models.address import Address
from app.models.user import User
from app.schemas.address import AddressCreate, AddressRead, AddressUpdate
from app.utils.address import get_address_or_404, clear_existing_default

router = APIRouter(prefix="/me/addresses", tags=["My Addresses"])


@router.post("", status_code=201, response_model=AddressRead)
def create_address(
    payload: AddressCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if payload.is_default_shipping:
        clear_existing_default(session, current_user.id, "is_default_shipping")
    if payload.is_default_billing:
        clear_existing_default(session, current_user.id, "is_default_billing")

    new_address = Address(**payload.model_dump(), user_id=current_user.id)
    session.add(new_address)
    session.commit()
    session.refresh(new_address)
    return new_address


@router.get("", response_model=List[AddressRead])
def list_addresses(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    statement = (
        select(Address)
        .where(Address.user_id == current_user.id)
        .order_by(Address.created_at.desc())
    )
    return session.exec(statement).all()


@router.get("/{address_id}", response_model=AddressRead)
def get_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return get_address_or_404(session, current_user.id, address_id)


@router.patch("/{address_id}", response_model=AddressRead)
def update_address(
    address_id: int,
    payload: AddressUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    address = get_address_or_404(session, current_user.id, address_id)
    updated_data = payload.model_dump(exclude_unset=True)

    if updated_data.get("is_default_shipping") is True:
        clear_existing_default(session, current_user.id, "is_default_shipping")
    if updated_data.get("is_default_billing") is True:
        clear_existing_default(session, current_user.id, "is_default_billing")

    for field, value in updated_data.items():
        setattr(address, field, value)

    address.updated_at = datetime.now(timezone.utc)
    session.add(address)
    session.commit()
    session.refresh(address)
    return address


@router.delete("/{address_id}", status_code=204)
def delete_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    address = get_address_or_404(session, current_user.id, address_id)
    session.delete(address)
    session.commit()