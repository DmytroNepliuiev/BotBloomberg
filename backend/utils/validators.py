# backend/utils/validators.py
from typing import Any, Dict

ALLOWED_STATUSES = {"closed", "open", "in_progress", "completed"}

def validate_status(status: str) -> bool:
    return status in ALLOWED_STATUSES

def participant_valid(p: Dict[str, Any]) -> bool:
    return isinstance(p.get("discord_id"), str) and isinstance(p.get("nickname"), str)

def reservation_valid(r: Dict[str, Any]) -> bool:
    return (r.get("nickname") is not None) and isinstance(r.get("nickname"), str)
