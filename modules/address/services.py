import logging
import math
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Address
from .schemas import AddressCreate, AddressUpdate

logger = logging.getLogger("address_book.address")


class AddressService:
    @staticmethod
    async def create(db: AsyncSession, data: AddressCreate) -> Address:
        logger.info("Creating address %s", data.name)
        query = select(Address).where(Address.name == data.name)
        result = await db.execute(query)
        if result.scalar_one_or_none():
            logger.warning("Address creation failed: duplicate name %s", data.name)
            raise ValueError("Address with that name already exists")

        address = Address(**data.model_dump())
        db.add(address)
        await db.commit()
        await db.refresh(address)
        logger.info("Address created %s", address.uuid)
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
        logger.debug(
            "Fetching addresses skip=%s limit=%s latitude=%s longitude=%s radius=%s",
            skip,
            limit,
            latitude,
            longitude,
            radius_km,
        )
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
        addresses = list(result.scalars().all())
        logger.info("Fetched %s addresses", len(addresses))
        return addresses

    @staticmethod
    async def get_one_by_uuid(db: AsyncSession, address_uuid: UUID) -> Address | None:
        logger.debug("Fetching address %s", address_uuid)
        result = await db.execute(select(Address).where(Address.uuid == address_uuid))
        address = result.scalar_one_or_none()
        if address is None:
            logger.warning("Address not found %s", address_uuid)
        return address

    @staticmethod
    async def update(
        db: AsyncSession, address_uuid: UUID, data: AddressUpdate
    ) -> Address | None:
        logger.info("Updating address %s", address_uuid)
        address = await AddressService.get_one_by_uuid(db, address_uuid)
        if not address:
            logger.warning("Update failed: address not found %s", address_uuid)
            return None

        if data.name is not None and data.name != address.name:
            query = select(Address).where(Address.name == data.name)
            result = await db.execute(query)
            if result.scalar_one_or_none():
                logger.warning(
                    "Update failed: duplicate address name %s for %s",
                    data.name,
                    address_uuid,
                )
                raise ValueError("Address with that name already exists")

        update_data = data.model_dump(exclude_unset=True)
        logger.debug("Update data for %s: %s", address_uuid, update_data)
        for key, value in update_data.items():
            setattr(address, key, value)

        await db.commit()
        await db.refresh(address)
        logger.info("Address updated %s", address_uuid)
        return address

    @staticmethod
    async def delete(db: AsyncSession, address_uuid: UUID) -> bool:
        logger.info("Deleting address %s", address_uuid)
        address = await AddressService.get_one_by_uuid(db, address_uuid)
        if not address:
            logger.warning("Delete failed: address not found %s", address_uuid)
            return False
        await db.delete(address)
        await db.commit()
        logger.info("Address deleted %s", address_uuid)
        return True
