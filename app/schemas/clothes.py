""" Schémas des vêtements """

from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime, date

from app.enums import Item, Size

class ClothingCreate(BaseModel):
    name: str
    item: Item
    size: Size
    price: float = Field(ge=0)
    description: str
    stock: int = Field(ge=0)


class ClothingUpdate(BaseModel):
    name: str | None = None
    item: Item | None = None
    size: Size | None = None
    price: float | None = Field(default=None, ge=0)
    description: str | None = None
    stock: int | None = Field(default=None, ge=0)
    is_featured: bool | None = None
    is_published: bool | None = None
    is_expired: bool | None = None


class ClothingRead(BaseModel):
    id: int
    name: str
    item: Item 
    size: Size 
    price: float 
    description: str 
    stock: int 
    is_featured: bool 
    is_published: bool 
    is_expired: bool 
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PublicClothingRead(BaseModel):
    id: int
    name: str
    item: Item 
    size: Size 
    price: float 
    description: str 
    is_expired: bool 

    model_config = ConfigDict(from_attributes=True)