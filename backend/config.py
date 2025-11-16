# backend/config.py
import os
from typing import List

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/contracts_db")
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", 8000))
DEBUG = os.getenv("DEBUG", "1") == "1"

# CORS
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")
if ALLOWED_ORIGINS != "*":
    ALLOWED_ORIGINS = [o.strip() for o in ALLOWED_ORIGINS.split(",")]

# Internal auth (optional) - used to secure internal endpoints called by bot
BACKEND_INTERNAL_KEY = os.getenv("BACKEND_INTERNAL_KEY", "")

# Contract defaults
DEFAULT_MAX_PARTICIPANTS = int(os.getenv("DEFAULT_MAX_PARTICIPANTS", "5"))
