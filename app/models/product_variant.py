""" Table des variations de produits """

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from app.enums import Size

if TYPE_CHECKING:
    from app.models.product import Product

class ProductVariant(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    size: Size
    stock: int
    price: float
    sku: str
    is_expired: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    product_id: int = Field(foreign_key="product.id", index=True)
    product: "Product" = Relationship(back_populates="variants")

   
