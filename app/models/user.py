""" Table des utilisateurs """

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone

from app.enums import UserRole


# ATTENTION PAR DEFAUT ADMIN, si autre type d'user, changer ce champ
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    email: str = Field(index=True, unique=True)
    password_hash: str

    role: UserRole = Field(default=UserRole.ADMIN)
    is_active: bool = Field(default=True)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))