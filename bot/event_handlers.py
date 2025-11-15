# bot/event_handlers.py
import discord
from discord.ext import commands
from .utils.logger import log_contract_event
from .config import CONTRACT_LOG_CHANNEL_ID

# Якщо ти хочеш імпортувати цей модуль як cog:
class EventCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        # додаткові дії при старті
        print("EventCog: ready")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # приклад логування
        print(f"Member joined: {member.display_name}")
