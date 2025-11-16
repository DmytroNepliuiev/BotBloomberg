# backend/routes/contract_routes.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..services.contract_service import (
    create_contract, get_contract, set_status, join_contract,
    reserve_name, remove_reservation, list_participants_and_reservations,
    get_all_contracts
)
from ..schemas.contract_schema import ContractCreate, ContractResponse, Participant, Reservation, StatusResponse
from ..config import BACKEND_INTERNAL_KEY

router = APIRouter(prefix="/contracts", tags=["contracts"])

# Public endpoints
@router.get("/", response_model=List[ContractResponse])
async def api_list_contracts(db: AsyncSession = Depends(get_db)):
    contracts = await get_all_contracts(db)
    return contracts

@router.get("/{contract_id}", response_model=ContractResponse)
async def api_get_contract(contract_id: int, db: AsyncSession = Depends(get_db)):
    contract = await get_contract(db, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract

@router.get("/{contract_id}/status", response_model=StatusResponse)
async def api_get_status(contract_id: int, db: AsyncSession = Depends(get_db)):
    contract = await get_contract(db, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return StatusResponse(
        id=contract.id,
        status=contract.status,
        participants_count=len(contract.participants or []),
        reservations_count=len(contract.reservations or [])
    )

# Internal endpoints (secured by BACKEND_INTERNAL_KEY header)
def _check_internal(request: Request):
    if BACKEND_INTERNAL_KEY:
        key = request.headers.get("Authorization")
        expected = f"Bearer {BACKEND_INTERNAL_KEY}"
        if key != expected:
            raise HTTPException(status_code=403, detail="Forbidden")

@router.post("/internal/create", dependencies=[Depends(_check_internal)])
async def internal_create_contract(payload: ContractCreate, db: AsyncSession = Depends(get_db)):
    contract = await create_contract(db, payload.type_contract)
    return {"id": contract.id, "status": contract.status}

@router.post("/internal/{contract_id}/start", dependencies=[Depends(_check_internal)])
async def internal_start_contract(contract_id: int, body: dict, db: AsyncSession = Depends(get_db)):
    contract = await get_contract(db, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    actor = body.get("started_by")
    contract = await set_status(db, contract, "open", actor_discord_id=actor)
    return {"ok": True, "status": contract.status}

@router.post("/internal/{contract_id}/close", dependencies=[Depends(_check_internal)])
async def internal_close_contract(contract_id: int, body: dict, db: AsyncSession = Depends(get_db)):
    contract = await get_contract(db, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    actor = body.get("closed_by")
    contract = await set_status(db, contract, "completed", actor_discord_id=actor)
    return {"ok": True, "status": contract.status}

@router.post("/internal/{contract_id}/join", dependencies=[Depends(_check_internal)])
async def internal_join(contract_id: int, body: dict, db: AsyncSession = Depends(get_db)):
    contract = await get_contract(db, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    discord_id = body.get("discord_id")
    nickname = body.get("nickname") or ""
    participant = Participant(discord_id=str(discord_id), nickname=nickname)
    ok, msg = await join_contract(db, contract, participant)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"ok": True, "message": msg}

@router.post("/internal/{contract_id}/reserve", dependencies=[Depends(_check_internal)])
async def internal_reserve(contract_id: int, body: dict, db: AsyncSession = Depends(get_db)):
    contract = await get_contract(db, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    discord_id = body.get("discord_id")
    nickname = body.get("reserved_name") or body.get("nickname") or ""
    reservation = Reservation(discord_id=str(discord_id) if discord_id else None, nickname=nickname)
    ok, msg = await reserve_name(db, contract, reservation)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"ok": True, "message": msg}

@router.post("/internal/{contract_id}/remove_reservation", dependencies=[Depends(_check_internal)])
async def internal_remove_reservation(contract_id: int, body: dict, db: AsyncSession = Depends(get_db)):
    contract = await get_contract(db, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    nickname = body.get("nickname")
    ok, msg = await remove_reservation(db, contract, nickname)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"ok": True, "message": msg}

@router.get("/{contract_id}/list")
async def api_get_list(contract_id: int, db: AsyncSession = Depends(get_db)):
    contract = await get_contract(db, contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return await list_participants_and_reservations(contract)
