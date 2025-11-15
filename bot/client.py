# bot/client.py
# Утримує логіку створення і конфігурації bot-обʼєкта.
import logging
import discord
from discord.ext import commands
from .config import DISCORD_BOT_TOKEN

logger = logging.getLogger("bot_client")

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

def setup_handlers():
    # тут можна імпортувати та реєструвати інші модулі/коги
    pass

def run():
    setup_handlers()
    bot.run(DISCORD_BOT_TOKEN)
