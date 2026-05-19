from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class AddressBase(BaseModel):
    name: str
    street: str
    sub_locality: str | None = None
    locality: str
    administrative_area: str | None = None
    postal_code: str | None = None
    country: str
    latitude: float
    longitude: float
    notes: str | None = None
    email: EmailStr | None = None
    phone_number: str | None = None
    website: str | None = None


class AddressCreate(AddressBase):
    pass


class AddressUpdate(BaseModel):
    name: str | None = None
    street: str | None = None
    sub_locality: str | None = None
    locality: str | None = None
    administrative_area: str | None = None
    postal_code: str | None = None
    country: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    notes: str | None = None
    email: EmailStr | None = None
    phone_number: str | None = None
    website: str | None = None


class AddressRead(AddressBase):
    uuid: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
