# bot/utils/logger.py
import discord
from ..config import CONTRACT_LOG_CHANNEL_ID

async def log_contract_event(bot: "discord.Client", title: str, description: str = None, embed: discord.Embed = None):
    """Відправити повідомлення-лог у вказаний канал (CONTRACT_LOG_CHANNEL_ID)."""
    if not CONTRACT_LOG_CHANNEL_ID:
        return
    channel = bot.get_channel(CONTRACT_LOG_CHANNEL_ID)
    if channel:
        if embed:
            await channel.send(embed=embed)
        else:
            await channel.send(f"**{title}**\n{description or ''}")
