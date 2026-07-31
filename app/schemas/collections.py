""" Schémas des collections """

from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime, date

class CollectionCreate(BaseModel):
    name: str
    start: datetime
    end: datetime | None = None


class CollectionUpdate(BaseModel):
    name: str | None = None
    start: datetime | None = None
    end: datetime | None = None
    is_published: bool | None = None


class CollectionRead(BaseModel):
    id: int
    name: str
    start: datetime
    end: datetime | None = None
    is_published: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PublicCollectionRead(BaseModel):
    id: int
    name: str
    start: datetime
    end: datetime | None = None

    model_config = ConfigDict(from_attributes=True)