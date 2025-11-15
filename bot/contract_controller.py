# bot/contract_controller.py
import aiohttp
from .config import BACKEND_URL, BACKEND_INTERNAL_KEY

_headers = {}
if BACKEND_INTERNAL_KEY:
    _headers["Authorization"] = f"Bearer {BACKEND_INTERNAL_KEY}"

async def start_contract(contract_id: int, started_by_discord_id: str):
    url = f"{BACKEND_URL}/internal/contracts/{contract_id}/start"
    payload = {"started_by": started_by_discord_id}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=_headers) as resp:
            text = await resp.text()
            try:
                data = await resp.json()
            except Exception:
                data = {"raw": text}
            return resp.status, data

async def close_contract(contract_id: int, closed_by_discord_id: str):
    url = f"{BACKEND_URL}/internal/contracts/{contract_id}/close"
    payload = {"closed_by": closed_by_discord_id}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=_headers) as resp:
            text = await resp.text()
            try:
                data = await resp.json()
            except Exception:
                data = {"raw": text}
            return resp.status, data

async def join_contract(contract_id: int, discord_id: str):
    url = f"{BACKEND_URL}/internal/contracts/{contract_id}/join"
    payload = {"discord_id": discord_id}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=_headers) as resp:
            text = await resp.text()
            try:
                data = await resp.json()
            except Exception:
                data = {"raw": text}
            return resp.status, data

async def reserve_name(contract_id: int, discord_id: str, reserved_name: str):
    url = f"{BACKEND_URL}/internal/contracts/{contract_id}/reserve"
    payload = {"discord_id": discord_id, "reserved_name": reserved_name}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=_headers) as resp:
            text = await resp.text()
            try:
                data = await resp.json()
            except Exception:
                data = {"raw": text}
            return resp.status, data

async def get_contract_status(contract_id: int):
    url = f"{BACKEND_URL}/internal/contracts/{contract_id}/status"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=_headers) as resp:
            try:
                data = await resp.json()
            except Exception:
                data = {"raw": await resp.text()}
            return resp.status, data
