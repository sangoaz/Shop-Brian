""" Table des produits """

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from app.enums import Item

if TYPE_CHECKING:
    from app.models.collections import Collection 
    from app.models.product_variant import ProductVariant

class Product(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    item: Item
    price: float
    description: str
    is_featured: bool = Field(default=True)
    is_published: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    images: list["ProductImage"] = Relationship(back_populates="product")

    collection_id: int = Field(foreign_key="collection.id", index=True)
    collection: "Collection" = Relationship(back_populates="products")
    variants: list["ProductVariant"] = Relationship(back_populates="product")


class ProductImage(SQLModel, table=True):
    id : int | None = Field(default=None, primary_key=True)
    image_url: str
    is_cover: bool = Field(default=True)
    display_order: int = Field(default=0)
    alt_text: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    product_id: int = Field(foreign_key="product.id", index=True)
    product: Product = Relationship(back_populates="images") 