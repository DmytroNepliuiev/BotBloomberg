# client/overlay/api.py
import aiohttp
import asyncio
from typing import Optional, Dict, Any, List
from .config import CONTRACTS_API, BACKEND_URL
from .state_manager import state

HEADERS_JSON = {"Content-Type": "application/json"}

def _auth_header() -> Dict[str, str]:
    token = state.get_token()
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}

async def fetch_contracts(session: aiohttp.ClientSession) -> List[Dict[str, Any]]:
    url = CONTRACTS_API
    headers = {**HEADERS_JSON, **_auth_header()}
    async with session.get(url, headers=headers) as resp:
        resp.raise_for_status()
        data = await resp.json()
        return data

async def fetch_contract_status(session: aiohttp.ClientSession, contract_id: int) -> Dict[str, Any]:
    url = f"{CONTRACTS_API}/{contract_id}/status"
    headers = {**HEADERS_JSON, **_auth_header()}
    async with session.get(url, headers=headers) as resp:
        resp.raise_for_status()
        return await resp.json()

async def start_contract(session: aiohttp.ClientSession, contract_id: int) -> Dict[str, Any]:
    url = f"{CONTRACTS_API}/internal/{contract_id}/start"
    headers = {**HEADERS_JSON, **_auth_header()}
    # internal endpoints on backend expect internal key; if not set, backend must allow this call
    payload = {"started_by": "client_unknown"}  # backend will normally accept bot identity; client uses JWT
    async with session.post(url, json=payload, headers=headers) as resp:
        # if backend returns 403 because internal key is required, this will error
        data = await resp.json()
        return {"status": resp.status, "data": data}

async def join_contract(session: aiohttp.ClientSession, contract_id: int, nickname: str) -> Dict[str, Any]:
    url = f"{CONTRACTS_API}/internal/{contract_id}/join"
    headers = {**HEADERS_JSON, **_auth_header()}
    payload = {"discord_id": None, "nickname": nickname}  # client can't put discord id if not known
    async with session.post(url, json=payload, headers=headers) as resp:
        data = await resp.json()
        return {"status": resp.status, "data": data}

async def reserve_name(session: aiohttp.ClientSession, contract_id: int, nickname: str) -> Dict[str, Any]:
    url = f"{CONTRACTS_API}/internal/{contract_id}/reserve"
    headers = {**HEADERS_JSON, **_auth_header()}
    payload = {"discord_id": None, "reserved_name": nickname}
    async with session.post(url, json=payload, headers=headers) as resp:
        data = await resp.json()
        return {"status": resp.status, "data": data}

# Synchronous wrappers for use from UI thread (runs simple asyncio loop in background)
def run_coro_in_bg(coro):
    return asyncio.run_coroutine_threadsafe(coro, _bg_loop)

# Background loop and client session management (set up by ui.py when launching background tasks)
_bg_loop: Optional[asyncio.AbstractEventLoop] = None
_bg_session: Optional[aiohttp.ClientSession] = None

def start_background_loop(loop: asyncio.AbstractEventLoop, session: aiohttp.ClientSession):
    global _bg_loop, _bg_session
    _bg_loop = loop
    _bg_session = session

def stop_background_loop():
    global _bg_loop, _bg_session
    if _bg_session:
        asyncio.run_coroutine_threadsafe(_bg_session.close(), _bg_loop)
    _bg_loop = None
    _bg_session = None
