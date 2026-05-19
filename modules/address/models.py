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

    # Neighborhood, district, barangay, or gated community
    sub_locality: Mapped[str | None]

    # City, town, or village
    locality: Mapped[str]

    # State, Province, Prefecture, or Region
    administrative_area: Mapped[str | None] = mapped_column(index=True)

    # ZIP code
    postal_code: Mapped[str | None] = mapped_column(index=True)

    country: Mapped[str] = mapped_column(index=True)
    latitude: Mapped[float]
    longitude: Mapped[float]

    # Additional optional fields for more detailed information about the address
    notes: Mapped[str | None]

    email: Mapped[str | None] = mapped_column(index=True)
    phone_number: Mapped[str | None] = mapped_column(index=True)
    website: Mapped[str | None]
