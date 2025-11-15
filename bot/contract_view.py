# bot/contract_view.py
import discord
from discord.ui import View, button, Button
from . import config
from .utils.permissions import user_has_role_by_name
from .contract_controller import start_contract, join_contract, reserve_name, get_contract_status
import asyncio

class ContractView(View):
    def __init__(self, author: discord.Member, contract_id: int):
        super().__init__(timeout=None)
        self.author = author
        self.contract_id = contract_id
        # стан локального кешу (отримувати з бекенду при ініціалізації)
        self.status = "closed"
        self.participants = []  # list of discord.Member (cached)
        self.reservations = []  # list of dicts {"name": str, "by": discord.Member or None}

    async def refresh_from_backend(self):
        code, data = await get_contract_status(self.contract_id)
        if code == 200:
            self.status = data.get("status", self.status)
            # за бажанням: оновити participants/reservations
            self.participants = []  # залишаємо пустим — бот чекає на оновлення через DB
            self.reservations = []
        return code, data

    def create_embed(self):
        if self.status == "closed":
            title = "Контракт закритий"
            description = "Можна розпочати контракт."
            embed = discord.Embed(title=title, description=description, color=discord.Color.dark_gray())
            embed.set_footer(text=f"Спробував запустити: {self.author.display_name}")
            return embed
        elif self.status == "open":
            title = "Контракт відкритий"
            description = "Триває набір учасників"
            embed = discord.Embed(title=title, description=description, color=discord.Color.orange())
            embed.add_field(name="Учасників (локально)", value=str(len(self.participants)))
            embed.add_field(name="Резерви (локально)", value=str(len(self.reservations)))
            embed.set_footer(text=f"Контракт відкрив: {self.author.display_name}")
            return embed
        elif self.status == "completed":
            title = "Контракт завершено"
            embed = discord.Embed(title=title, description="Дякуємо за участь!", color=discord.Color.green())
            return embed

    # кнопки:
    @button(label="Розпочати контракт?", style=discord.ButtonStyle.primary, custom_id="start_contract")
    async def start_contract_button(self, interaction: discord.Interaction, button: Button):
        # перевіряємо роль
        if not user_has_role_by_name(interaction.user, config.CONTRACT_ROLE_NAME):
            await interaction.response.send_message("У вас немає ролі для запуску контракту.", ephemeral=True)
            return

        # виклик до бекенду
        status, data = await start_contract(self.contract_id, str(interaction.user.id))
        if status == 200:
            self.status = "open"
            embed = self.create_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.send_message(f"Не вдалося розпочати контракт: {data}", ephemeral=True)

    @button(label="Прийняти участь", style=discord.ButtonStyle.success, custom_id="join_contract")
    async def join_contract_button(self, interaction: discord.Interaction, button: Button):
        # виклик бекенду
        status, data = await join_contract(self.contract_id, str(interaction.user.id))
        if status == 200:
            # можна додати локальний кеш
            self.participants.append(interaction.user)
            embed = self.create_embed()
            await interaction.response.edit_message(embed=embed, view=self)
            await interaction.followup.send("Ви додані до списку учасників.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Не вдалося приєднатись: {data}", ephemeral=True)

    @button(label="Зарезервувати нік", style=discord.ButtonStyle.secondary, custom_id="reserve_name")
    async def reserve_button(self, interaction: discord.Interaction, button: Button):
        # відкриваємо modal для вводу ніку
        modal = ReserveModal(self.contract_id)
        await interaction.response.send_modal(modal)

class ReserveModal(discord.ui.Modal, title="Зарезервувати нік"):
    name = discord.ui.TextInput(label="Нік персонажа", placeholder="Введіть нік", max_length=32)

    def __init__(self, contract_id: int):
        super().__init__()
        self.contract_id = contract_id

    async def on_submit(self, interaction: discord.Interaction):
        status, data = await reserve_name(self.contract_id, str(interaction.user.id), self.name.value)
        if status == 200:
            await interaction.response.send_message("Нік зарезервовано.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Помилка резерву: {data}", ephemeral=True)
