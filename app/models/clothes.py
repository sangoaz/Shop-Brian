""" Table des vetements """

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from app.enums import Item, Size

if TYPE_CHECKING:
    from app.models.collections import Collection 

class Clothing(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    item: Item
    size: Size
    price: float
    description: str
    stock: int
    is_featured: bool = Field(default=True)
    is_published: bool = Field(default=True)
    is_expired: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    images: list["ClothingImage"] = Relationship(back_populates="clothing")

    collection_id: int = Field(foreign_key="collection.id", index=True)
    collection: "Collection" = Relationship(back_populates="clothes")

class ClothingImage(SQLModel, table=True):
    id : int | None = Field(default=None, primary_key=True)
    image_url: str
    is_cover: bool = Field(default=True)
    display_order: int = Field(default=0)
    alt_text: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    clothing_id: int = Field(foreign_key="clothing.id", index=True)
    clothing: Clothing = Relationship(back_populates="images")    
