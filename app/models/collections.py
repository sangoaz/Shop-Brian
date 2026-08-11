""" Table des collections """

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.product import Product

class Collection(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    start: datetime | None = Field(default_factory=lambda: datetime.now(timezone.utc))
    end: datetime | None = None
    is_published: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    products: list["Product"] = Relationship(back_populates="collection")
    images: list["CollectionImage"] = Relationship(back_populates="collection")

class CollectionImage(SQLModel, table=True):
    id : int | None = Field(default=None, primary_key=True)
    image_url: str
    is_cover: bool = Field(default=True)
    display_order: int = Field(default=0)
    alt_text: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    collection_id: int = Field(foreign_key="collection.id", index=True)
    collection: Collection = Relationship(back_populates="images")

