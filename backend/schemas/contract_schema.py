# backend/schemas/contract_schema.py
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict
from datetime import datetime

class Participant(BaseModel):
    discord_id: str = Field(..., example="123456789012345678")
    nickname: str = Field(..., example="Ari Bloomberg")

class Reservation(BaseModel):
    discord_id: Optional[str] = Field(None, example="123456789012345678")
    nickname: str = Field(..., example="Ari Bloomberg")

class ContractCreate(BaseModel):
    type_contract: str = Field(..., example="medical")
    max_participants: Optional[int] = Field(None, example=5)

class ContractUpdate(BaseModel):
    status: Optional[str] = Field(None, example="open")
    type_contract: Optional[str] = None

class ContractResponse(BaseModel):
    id: int
    type_contract: str
    status: str
    participants: List[Participant]
    reservations: List[Reservation]
    opened_by: Optional[str]
    closed_by: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class StatusResponse(BaseModel):
    id: int
    status: str
    participants_count: int
    reservations_count: int
