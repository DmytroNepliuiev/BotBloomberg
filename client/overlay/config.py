# client/overlay/config.py
import os

# Backend base URL (FastAPI)
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# OAuth: backend login endpoint to open in browser.
# Backend should redirect to LOCAL_CALLBACK_URL with token param.
OAUTH_LOGIN_URL = f"{BACKEND_URL}/auth/discord/login"

# Local callback URL (client listens on this port to receive JWT)
LOCAL_CALLBACK_HOST = "127.0.0.1"
LOCAL_CALLBACK_PORT = int(os.getenv("LOCAL_CALLBACK_PORT", "8765"))
LOCAL_CALLBACK_URL = f"http://{LOCAL_CALLBACK_HOST}:{LOCAL_CALLBACK_PORT}/callback"

# WebSocket URL for receiving updates (ws or wss)
WEBSOCKET_URL = os.getenv("WEBSOCKET_URL", f"ws://127.0.0.1:8000/ws/contracts")

# API endpoints
CONTRACTS_API = f"{BACKEND_URL}/contracts"

# UI settings
WINDOW_WIDTH = 360
WINDOW_HEIGHT = 420

# Toggle debug logs
DEBUG = os.getenv("OVERLAY_DEBUG", "1") == "1"
