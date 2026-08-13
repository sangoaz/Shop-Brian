""" Table des utilisateurs """

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone

from app.enums import UserRole


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    email: str = Field(index=True, unique=True)
    password_hash: str

    role: UserRole = Field(default=UserRole.CUSTOMER)
    is_active: bool = Field(default=True)

    reset_token_hash: str | None = Field(default=None, index=True)
    reset_token_expires_at: datetime | None = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))