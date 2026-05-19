from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from typing import Optional
import pycountry
import phonenumbers
import re


class AddressBase(BaseModel):
    name: str
    street: str
    sub_locality: str | None = Field(
        default=None,
        description="Neighborhood, district, barangay, or gated community",
    )
    locality: str = Field(description="City, town, or village")
    administrative_area: str | None = Field(
        default=None,
        description="State, Province, Prefecture, or Region",
    )
    postal_code: str | None = Field(default=None, description="ZIP/Postal code")
    country: str
    latitude: float
    longitude: float
    notes: str | None = None
    email: EmailStr | None = None
    phone_number: str | None = None
    website: str | None = None


class AddressCreate(AddressBase):
    @field_validator('country')
    @classmethod
    def validate_country_code(cls, v: str) -> str:
        if pycountry.countries.get(alpha_2=v.upper()) is None:
            raise ValueError("Invalid country code. Must be ISO 3166-1 alpha-2.")
        return v.upper()

    @field_validator('postal_code')
    @classmethod
    def validate_postal_code(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # This regex allows letters, numbers, spaces, and hyphens, with a length of 2-10.
        if not re.fullmatch(r"^[a-zA-Z0-9\s-]{2,10}$", v):
            raise ValueError("Invalid postal code format.")
        return v

    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            # Must start with '+'
            if not v.startswith('+'):
                raise ValueError("Phone number must start with '+' for E.164 format (e.g., +1234567890).")
            parsed_number = phonenumbers.parse(v)
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValueError("Invalid phone number format.")
            return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            raise ValueError("Invalid phone number format.")


class AddressUpdate(BaseModel):
    name: str | None = None
    street: str | None = None
    sub_locality: str | None = None
    locality: str | None = None
    administrative_area: str | None = None
    postal_code: str | None = None
    country: str | None = None
    latitude: Optional[float] = Field(default=None, ge=-90, le=90, description="Latitude in decimal degrees (-90 to 90)")
    longitude: Optional[float] = Field(default=None, ge=-180, le=180, description="Longitude in decimal degrees (-180 to 180)")
    notes: str | None = None
    email: EmailStr | None = None
    phone_number: str | None = None
    website: str | None = None

    @field_validator('country')
    @classmethod
    def validate_country_code(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if pycountry.countries.get(alpha_2=v.upper()) is None:
            raise ValueError("Invalid country code. Must be ISO 3166-1 alpha-2 (e.g., 'US' for the United States).")
        return v.upper()

    @field_validator('postal_code')
    @classmethod
    def validate_postal_code(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not re.fullmatch(r"^[a-zA-Z0-9\s-]{2,10}$", v):
            raise ValueError("Invalid postal code format.")
        return v

    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            if not v.startswith('+'):
                raise ValueError("Phone number must start with '+' for E.164 format (e.g., +1234567890).")
            parsed_number = phonenumbers.parse(v)
            if not phonenumbers.is_valid_number(parsed_number):
                raise ValueError("Invalid phone number format.")
            return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            raise ValueError("Invalid phone number format.")


class AddressRead(AddressBase):
    uuid: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
