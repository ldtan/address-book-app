from sqlalchemy import Index
from sqlalchemy.orm import Mapped, mapped_column

from core.mixins import DatetimeTrackerMixin, UUIDMixin
from core.models import BaseModel


class Address(BaseModel, UUIDMixin, DatetimeTrackerMixin):
    __tablename__ = "addresses"

    __table_args__ = (
        # A composite index on coordinates makes geospatial queries
        # (like finding nearby locations) much faster later on.
        Index("ix_addresses_coordinates", "latitude", "longitude"),
    )

    name: Mapped[str] = mapped_column(unique=True, index=True)
    street: Mapped[str]
    sub_locality: Mapped[str | None]
    locality: Mapped[str]
    administrative_area: Mapped[str | None] = mapped_column(index=True)
    postal_code: Mapped[str | None] = mapped_column(index=True)
    country: Mapped[str] = mapped_column(index=True)
    latitude: Mapped[float]
    longitude: Mapped[float]
    notes: Mapped[str | None]

    email: Mapped[str | None] = mapped_column(index=True)
    phone_number: Mapped[str | None] = mapped_column(index=True)
    website: Mapped[str | None]
