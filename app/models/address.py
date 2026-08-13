""" Table des adresses """

import sqlalchemy as sa
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Index
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User

class Address(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    full_name: str
    address_line1: str
    address_line2: str | None = None
    postal_code: str
    city: str
    country: str = Field(default="FR")
    phone: str

    is_default_shipping: bool = Field(default=False)
    is_default_billing: bool = Field(default=False)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user_id: int = Field(foreign_key="user.id", index=True)
    user: "User" = Relationship(back_populates="addresses")

    __table_args__ = (
        Index(
            "ix_address_one_default_shipping_per_user",
            "user_id",
            unique=True,
            postgresql_where=sa.text("is_default_shipping = true"),
        ),
        Index(
            "ix_address_one_default_billing_per_user",
            "user_id",
            unique=True,
            postgresql_where=sa.text("is_default_billing = true"),
        ),
    )