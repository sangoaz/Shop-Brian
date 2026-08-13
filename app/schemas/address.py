""" Schémas des adresses """

from pydantic import BaseModel, ConfigDict
from datetime import datetime

class AddressCreate(BaseModel):
    full_name: str
    address_line1: str
    address_line2: str | None = None
    postal_code: str
    city: str
    country: str = "FR"
    phone: str
    is_default_shipping: bool = False
    is_default_billing: bool = False


class AddressUpdate(BaseModel):
    full_name: str | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    postal_code: str | None = None
    city: str | None = None
    country: str | None = None
    phone: str | None = None
    is_default_shipping: bool | None = None
    is_default_billing: bool | None = None


class AddressRead(BaseModel):
    id: int
    full_name: str
    address_line1: str
    address_line2: str | None
    postal_code: str
    city: str
    country: str
    phone: str
    is_default_shipping: bool
    is_default_billing: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)