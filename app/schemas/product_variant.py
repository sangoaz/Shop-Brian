""" Schéma des variantes des produits """

from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

from app.enums import Size

class VariantCreate(BaseModel):
    size: Size
    stock: int = Field(ge=0)
    price_override: float | None = Field(default=None, ge=0)
    sku: str


class VariantUpdate(BaseModel):
    size: Size | None = None
    stock: int | None = Field(default=None, ge=0)
    price_override: float | None = Field(default=None, ge=0)
    sku: str | None = None
    is_expired: bool | None = None


class VariantRead(BaseModel):
    id: int
    size: Size
    stock: int
    price_override: float | None
    sku: str
    is_expired: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PublicVariantRead(BaseModel):
    id: int
    size: Size
    price: float = Field(validation_alias="effective_price")
    is_expired: bool

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)