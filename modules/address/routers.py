from fastapi import APIRouter

router = APIRouter(prefix="/addresses", tags=["Addresses"])


@router.get("/")
async def get_addresses():
    return {"message": "List of addresses"}


@router.post("/")
async def create_address():
    return {"message": "Address created"}


@router.get("/{address_id}")
async def get_address(address_id: int):
    return {"message": f"Details of address {address_id}"}


@router.put("/{address_id}")
async def update_address(address_id: int):
    return {"message": f"Address {address_id} updated"}


@router.delete("/{address_id}")
async def delete_address(address_id: int):
    return {"message": f"Address {address_id} deleted"}
