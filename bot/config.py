import os
from dotenv import load_dotenv

# 1. ЗАВАНТАЖЕННЯ:
# Завантажуємо змінні середовища з файлу .env, який повинен знаходитися
# у корені проєкту. Це необхідно, щоб os.getenv() міг прочитати значення.
load_dotenv() 

# Discord / bot
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
# 2. ВИПРАВЛЕННЯ: Використовуємо ANNOUNCE_CHANNEL_ID, як визначено у .env
ANNOUNCE_CHANNEL_ID = int(os.getenv("ANNOUNCE_CHANNEL_ID", "0"))
CONTRACT_LOG_CHANNEL_ID = int(os.getenv("CONTRACT_LOG_CHANNEL_ID", "0"))
CONTRACT_ROLE_NAME = os.getenv("CONTRACT_ROLE_NAME", "Контракт")

# Backend
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")  # адреса бекенду
BACKEND_INTERNAL_KEY = os.getenv("BACKEND_INTERNAL_KEY", "")  # для internal-запитів (опційно)

# Internal HTTP server (для приймання запитів від бекенду)
INTERNAL_HTTP_HOST = os.getenv("INTERNAL_HTTP_HOST", "0.0.0.0")
INTERNAL_HTTP_PORT = int(os.getenv("INTERNAL_HTTP_PORT", "8080"))