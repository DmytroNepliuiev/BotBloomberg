# bot/utils/permissions.py
from discord import utils

def user_has_role_by_name(member: "discord.Member", role_name: str) -> bool:
    """Перевірити наявність ролі у member по імені ролі."""
    if not member:
        return False
    role = utils.get(member.guild.roles, name=role_name)
    if role is None:
        return False
    return role in member.roles
