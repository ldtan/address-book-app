import uuid
from datetime import UTC, datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, declared_attr, mapped_column


class UUIDMixin:
    @declared_attr
    def uuid(cls) -> Mapped[uuid.UUID]:
        return mapped_column(sa.Uuid, unique=True, default=uuid.uuid7)


class DatetimeTrackerMixin:
    @declared_attr
    def created_at(cls) -> Mapped[sa.DateTime]:
        return mapped_column(
            sa.DateTime(timezone=True),
            default=lambda: datetime.now(UTC),
        )

    @declared_attr
    def updated_at(cls) -> Mapped[sa.DateTime]:
        return mapped_column(
            sa.DateTime(timezone=True),
            default=lambda: datetime.now(UTC),
            onupdate=lambda: datetime.now(UTC),
        )

    @declared_attr
    def deleted_at(cls) -> Mapped[sa.DateTime | None]:
        return mapped_column(sa.DateTime(timezone=True), nullable=True)
