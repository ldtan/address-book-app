import sqlalchemy as sa
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from infrastructure.database import Base


class BaseModel(Base):
    __abstract__ = True

    @declared_attr
    def id(cls) -> Mapped[int]:
        return mapped_column(sa.Integer, primary_key=True)
