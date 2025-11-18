# backend/websocket/ws_manager.py
from fastapi import WebSocket
from typing import List
import asyncio
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)

    async def send_personal_message(self, websocket: WebSocket, message: dict):
        await websocket.send_json(message)

    async def broadcast(self, message: dict):
        data = json.dumps(message)
        async with self._lock:
            conns = list(self.active_connections)
        for connection in conns:
            try:
                await connection.send_text(data)
            except Exception:
                # ignore / or schedule disconnect
                pass

manager = ConnectionManager()
