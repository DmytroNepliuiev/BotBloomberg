# backend/services/contract_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from ..models.contract import Contract
from ..schemas.contract_schema import Participant, Reservation
from typing import List, Optional, Tuple
from datetime import datetime
from ..config import DEFAULT_MAX_PARTICIPANTS
import json

ALLOWED_STATUSES = {"closed", "open", "in_progress", "completed"}

async def create_contract(db: AsyncSession, type_contract: str) -> Contract:
    contract = Contract(
        type_contract=type_contract,
        status="closed",
        participants=[],
        reservations=[]
    )
    db.add(contract)
    await db.commit()
    await db.refresh(contract)
    return contract

async def get_contract(db: AsyncSession, contract_id: int) -> Optional[Contract]:
    q = await db.execute(select(Contract).where(Contract.id == contract_id))
    return q.scalar_one_or_none()

async def get_all_contracts(db: AsyncSession) -> List[Contract]:
    q = await db.execute(select(Contract).order_by(Contract.created_at.desc()))
    return q.scalars().all()

async def set_status(db: AsyncSession, contract: Contract, status: str, actor_discord_id: Optional[str] = None) -> Contract:
    if status not in ALLOWED_STATUSES:
        raise ValueError("Invalid status")
    contract.status = status
    if status == "open":
        contract.opened_by = actor_discord_id
        contract.closed_by = None
    if status == "completed" or status == "closed":
        contract.closed_by = actor_discord_id
    contract.updated_at = datetime.utcnow()
    db.add(contract)
    await db.commit()
    await db.refresh(contract)
    return contract

async def join_contract(db: AsyncSession, contract: Contract, participant: Participant, max_participants: Optional[int] = None) -> Tuple[bool, str]:
    """Add participant if not present and if capacity allows."""
    if contract.status not in ("open", "in_progress"):
        return False, "Contract is not open for joining"
    max_p = max_participants or DEFAULT_MAX_PARTICIPANTS
    cur = contract.participants or []
    # check duplicate by discord_id
    if any(p.get("discord_id") == participant.discord_id for p in cur):
        return False, "Already joined"
    if len(cur) >= max_p:
        return False, "No available slots"
    cur.append({"discord_id": participant.discord_id, "nickname": participant.nickname})
    contract.participants = cur
    contract.updated_at = datetime.utcnow()
    db.add(contract)
    await db.commit()
    await db.refresh(contract)
    return True, "Joined"

async def reserve_name(db: AsyncSession, contract: Contract, reservation: Reservation) -> Tuple[bool, str]:
    cur = contract.reservations or []
    # allow multiple reservations with same nickname but track discord_id
    cur.append({"discord_id": reservation.discord_id, "nickname": reservation.nickname})
    contract.reservations = cur
    contract.updated_at = datetime.utcnow()
    db.add(contract)
    await db.commit()
    await db.refresh(contract)
    return True, "Reserved"

async def remove_reservation(db: AsyncSession, contract: Contract, nickname: str) -> Tuple[bool, str]:
    cur = contract.reservations or []
    new = [r for r in cur if r.get("nickname") != nickname]
    if len(new) == len(cur):
        return False, "Reservation not found"
    contract.reservations = new
    contract.updated_at = datetime.utcnow()
    db.add(contract)
    await db.commit()
    await db.refresh(contract)
    return True, "Removed"

async def list_participants_and_reservations(contract: Contract):
    return {
        "participants": contract.participants or [],
        "reservations": contract.reservations or []
    }
