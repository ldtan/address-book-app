import math
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Address
from .schemas import AddressCreate, AddressUpdate


class AddressService:
    @staticmethod
    async def create(db: AsyncSession, data: AddressCreate) -> Address:
        query = select(Address).where(Address.name == data.name)
        result = await db.execute(query)
        if result.scalar_one_or_none():
            raise ValueError("Address with that name already exists")

        address = Address(**data.model_dump())
        db.add(address)
        await db.commit()
        await db.refresh(address)
        return address

    @staticmethod
    async def get_many(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        latitude: float | None = None,
        longitude: float | None = None,
        radius_km: float | None = None,
    ) -> list[Address]:
        stmt = select(Address)

        # Nearby location filtering
        if latitude is not None and longitude is not None and radius_km is not None:
            # Approximate 1 degree of latitude = 111km
            lat_delta = radius_km / 111.0
            # 1 degree of longitude = 111km * cos(latitude)
            lng_delta = radius_km / (111.0 * math.cos(math.radians(latitude)))

            stmt = stmt.where(
                Address.latitude.between(latitude - lat_delta, latitude + lat_delta),
                Address.longitude.between(longitude - lng_delta, longitude + lng_delta),
            )

        result = await db.execute(stmt.offset(skip).limit(limit))
        return list(result.scalars().all())

    @staticmethod
    async def get_one_by_uuid(db: AsyncSession, address_uuid: UUID) -> Address | None:
        result = await db.execute(select(Address).where(Address.uuid == address_uuid))
        return result.scalar_one_or_none()

    @staticmethod
    async def update(
        db: AsyncSession, address_uuid: UUID, data: AddressUpdate
    ) -> Address | None:
        address = await AddressService.get_one_by_uuid(db, address_uuid)
        if not address:
            return None

        if data.name is not None and data.name != address.name:
            query = select(Address).where(Address.name == data.name)
            result = await db.execute(query)
            if result.scalar_one_or_none():
                raise ValueError("Address with that name already exists")

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(address, key, value)

        await db.commit()
        await db.refresh(address)
        return address

    @staticmethod
    async def delete(db: AsyncSession, address_uuid: UUID) -> bool:
        address = await AddressService.get_one_by_uuid(db, address_uuid)
        if not address:
            return False
        await db.delete(address)
        await db.commit()
        return True
