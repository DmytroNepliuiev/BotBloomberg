# bot/bot.py
import asyncio
import logging
from aiohttp import web
import discord
from discord.ext import commands

from .config import (
    DISCORD_BOT_TOKEN,
    ANNOUNCE_CHANNEL_ID,
    INTERNAL_HTTP_HOST,
    INTERNAL_HTTP_PORT,
    CONTRACT_LOG_CHANNEL_ID,
)
from .contract_view import ContractView
from .utils.logger import log_contract_event

logger = logging.getLogger("bot")
logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True  # не потрібно зазвичай, став True якщо треба

bot = commands.Bot(command_prefix="!", intents=intents)


# Events
@bot.event
async def on_ready():
    logger.info(f"Bot ready: {bot.user} (guilds: {len(bot.guilds)})")


# Простий command для створення ContractView-повідомлення:
@bot.command(name="newcontract")
@commands.has_permissions(manage_guild=True)
async def cmd_newcontract(ctx, contract_id: int = 1):
    view = ContractView(author=ctx.author, contract_id=contract_id)
    # синхронно підвантажимо стан з бекенду (необов'язково)
    await view.refresh_from_backend()
    embed = view.create_embed()
    msg = await ctx.send(embed=embed, view=view)
    # збережемо id повідомлення у локальний атрибут (можна зберегти у бекенд пізніше)
    view.message_id = msg.id


# Internal HTTP endpoint(s) для бекенду
async def handle_internal_announce(request):
    """
    POST /internal/announce
    JSON:
    { "title": "...", "body": "...", "channel_id": <optional> }
    """
    try:
        data = await request.json()
    except Exception:
        return web.json_response({"error": "invalid json"}, status=400)

    channel_id = data.get("channel_id", ANNOUNCE_CHANNEL_ID)
    title = data.get("title", "")
    body = data.get("body", "")
    channel = bot.get_channel(channel_id)
    if not channel:
        return web.json_response({"error": "channel not found"}, status=404)
    embed = discord.Embed(title=title, description=body)
    await channel.send(embed=embed)
    return web.json_response({"ok": True})


async def start_internal_http():
    app = web.Application()
    app.router.add_post("/internal/announce", handle_internal_announce)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, INTERNAL_HTTP_HOST, INTERNAL_HTTP_PORT)
    await site.start()
    logger.info(f"Internal HTTP server started on {INTERNAL_HTTP_HOST}:{INTERNAL_HTTP_PORT}")


def main():
    loop = asyncio.get_event_loop()
    loop.create_task(start_internal_http())
    bot.run(DISCORD_BOT_TOKEN)


if __name__ == "__main__":
    main()
