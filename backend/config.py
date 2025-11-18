import os
from typing import List
from dotenv import load_dotenv

# На початку конфігураційного файлу завантажуємо змінні з .env
load_dotenv()

# --- Конфігурація PostgreSQL ---
# Читаємо окремі змінні, як визначено у вашому .env
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "contracts")

# Конструюємо повний DATABASE_URL з отриманих змінних
DATABASE_URL = (
    f"postgresql+asyncpg://"
    f"{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}"
    f"/{POSTGRES_DB}"
)

# --- API Backend ---
APP_HOST = os.getenv("API_HOST", "0.0.0.0") # Змінено з APP_HOST на API_HOST
APP_PORT = int(os.getenv("API_PORT", 8000))  # Змінено з APP_PORT на API_PORT
DEBUG = os.getenv("DEBUG", "1") == "1"

# CORS
ALLOWED_ORIGINS_RAW = os.getenv("ALLOWED_ORIGINS", "*")
if ALLOWED_ORIGINS_RAW == "*":
    ALLOWED_ORIGINS: List[str] = ["*"]
else:
    ALLOWED_ORIGINS = [o.strip() for o in ALLOWED_ORIGINS_RAW.split(",")]

# Internal auth
BACKEND_INTERNAL_KEY = os.getenv("INTERNAL_API_SECRET", "") 

# Contract defaults
DEFAULT_MAX_PARTICIPANTS = int(os.getenv("DEFAULT_MAX_PARTICIPANTS", "5"))