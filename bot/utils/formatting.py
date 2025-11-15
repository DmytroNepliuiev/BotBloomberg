# bot/utils/formatting.py
import discord

def make_contract_embed_simple(title: str, description: str = "", color: discord.Color = discord.Color.blue()):
    embed = discord.Embed(title=title, description=description, color=color)
    return embed
