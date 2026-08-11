""" Schémas des produits """

from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

from app.enums import Item
from app.schemas.product_variant import PublicVariantRead

class ProductCreate(BaseModel):
    name: str
    item: Item
    description: str
    price: float = Field(ge=0)


class ProductUpdate(BaseModel):
    name: str | None = None
    item: Item | None = None
    description: str | None = None
    price: float | None = Field(default=None, ge=0)
    is_featured: bool | None = None
    is_published: bool | None = None


class ProductRead(BaseModel):
    id: int
    name: str
    item: Item 
    description: str 
    is_featured: bool 
    price: float
    is_published: bool 
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PublicProductRead(BaseModel):
    id: int
    name: str
    item: Item 
    description: str 
    price: float
    variants: list[PublicVariantRead]

    model_config = ConfigDict(from_attributes=True)