from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.exc import DuplicateValueError
from infrastructure.database import get_db

from .schemas import AddressCreate, AddressRead, AddressUpdate
from .services import AddressService

router = APIRouter(prefix="/addresses", tags=["Addresses"])

DBDep = Annotated[AsyncSession, Depends(get_db)]


@router.get("/", response_model=list[AddressRead])
async def get_addresses(
    db: DBDep,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    lat: float | None = Query(default=None, ge=-90, le=90),
    lon: float | None = Query(default=None, ge=-180, le=180),
    radius: float | None = Query(default=None, ge=0),
    name: str | None = None,
    admin_area: str | None = None,
    postal_code: str | None = None,
    country: str | None = None,
):
    try:
        return await AddressService.get_many(
            db,
            skip=skip,
            limit=limit,
            latitude=lat,
            longitude=lon,
            radius_km=radius,
            name=name,
            administrative_area=admin_area,
            postal_code=postal_code,
            country=country,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/", response_model=AddressRead, status_code=status.HTTP_201_CREATED)
async def create_address(db: DBDep, address_in: AddressCreate):
    try:
        return await AddressService.create(db, address_in)
    except DuplicateValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{address_uuid}", response_model=AddressRead)
async def get_address(db: DBDep, address_uuid: UUID):
    address = await AddressService.get_one_by_uuid(db, address_uuid)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    return address


@router.put("/{address_uuid}", response_model=AddressRead)
async def update_address(db: DBDep, address_uuid: UUID, address_in: AddressUpdate):
    try:
        address = await AddressService.update(db, address_uuid, address_in)
    except DuplicateValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    return address


@router.delete("/{address_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(db: DBDep, address_uuid: UUID):
    success = await AddressService.delete(db, address_uuid)
    if not success:
        raise HTTPException(status_code=404, detail="Address not found")
    return None
