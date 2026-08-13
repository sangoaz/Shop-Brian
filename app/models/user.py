""" Table des utilisateurs """

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from app.enums import UserRole

if TYPE_CHECKING:
    from app.models.address import Address

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    email: str = Field(index=True, unique=True)
    password_hash: str

    role: UserRole = Field(default=UserRole.CUSTOMER)
    is_active: bool = Field(default=True)

    reset_token_hash: str | None = Field(default=None, index=True)
    reset_token_expires_at: datetime | None = None

    email_verified: bool = Field(default=False)
    verification_token_hash: str | None = Field(default=None, index=True)
    verification_token_expires_at: datetime | None = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    addresses: list["Address"] = Relationship(back_populates="user")