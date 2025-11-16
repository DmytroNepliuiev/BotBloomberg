# backend/main.py
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from .config import APP_HOST, APP_PORT, DEBUG, ALLOWED_ORIGINS
from .database import init_db, get_db
from .routes.contract_routes import router as contract_router
from .websocket.ws_manager import manager
from .utils.logger import logger

app = FastAPI(title="Contracts Backend")

# CORS
if ALLOWED_ORIGINS == "*":
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
else:
    app.add_middleware(CORSMiddleware, allow_origins=ALLOWED_ORIGINS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(contract_router)

@app.on_event("startup")
async def startup():
    logger.info("Initializing DB...")
    await init_db()
    logger.info("DB initialized.")

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.websocket("/ws/contracts")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()  # simple echo/receive - clients can send pings or subscribe messages
            # we can implement subscription logic; for now respond an ack
            await websocket.send_text(f"ack:{data}")
    except WebSocketDisconnect:
        await manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host=APP_HOST, port=APP_PORT, reload=DEBUG)
