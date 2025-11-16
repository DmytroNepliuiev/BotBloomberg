# backend/models/contract.py
from sqlalchemy import Column, Integer, Text, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from ..database import Base

class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type_contract = Column(Text, nullable=False, default="default")
    status = Column(Text, nullable=False, default="closed")   # closed/open/in_progress/completed
    participants = Column(JSONB, nullable=False, default=list)  # list of {"discord_id": str, "nickname": str}
    reservations = Column(JSONB, nullable=False, default=list)  # list of {"discord_id": str, "nickname": str}
    opened_by = Column(Text, nullable=True)
    closed_by = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
