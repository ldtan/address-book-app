from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database import get_db

from .schemas import AddressCreate, AddressRead, AddressUpdate
from .services import AddressService

router = APIRouter(prefix="/addresses", tags=["Addresses"])

DBDep = Annotated[AsyncSession, Depends(get_db)]


@router.get("/", response_model=list[AddressRead])
async def get_addresses(
    db: DBDep,
    skip: int = 0,
    limit: int = 100,
    lat: float | None = None,
    lon: float | None = None,
    radius: float | None = None,
):
    return await AddressService.get_many(
        db, skip=skip, limit=limit, latitude=lat, longitude=lon, radius_km=radius
    )


@router.post("/", response_model=AddressRead, status_code=status.HTTP_201_CREATED)
async def create_address(db: DBDep, address_in: AddressCreate):
    return await AddressService.create(db, address_in)


@router.get("/{address_uuid}", response_model=AddressRead)
async def get_address(db: DBDep, address_uuid: UUID):
    address = await AddressService.get_one_by_uuid(db, address_uuid)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    return address


@router.put("/{address_uuid}", response_model=AddressRead)
async def update_address(db: DBDep, address_uuid: UUID, address_in: AddressUpdate):
    address = await AddressService.update(db, address_uuid, address_in)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    return address


@router.delete("/{address_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(db: DBDep, address_uuid: UUID):
    success = await AddressService.delete(db, address_uuid)
    if not success:
        raise HTTPException(status_code=404, detail="Address not found")
    return None
