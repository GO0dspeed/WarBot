import discord
from discord.ext import commands
from discord import Intents
from tinydb import TinyDB
import logging
from config.config import Config
import asyncio

class WarBot(commands.bot):
    def __init__(
            self,
            *args,
            intents: Intents,
            db = TinyDB("data/db-squads.json"),
            config = Config()
    ):
        
        intents = Intents.default()
        intents.members = True
        intents.message_content = True

        super().__init__(intents=intents, command_prefix = "!")

        async def on_ready(self):
            await self.load_extension("extensions.configCog")
            await self.load_extension("extensions.warCog")
            await self.load_extension("extensions.statCog")
            self.wait_until_ready()
            print(f'Logged on as {self.user}')

        async def on_guild_join(self, guild: discord.Guild):
            await db.table(guild)

        async def on_guild_remove(self, guild: discord.Guild):
            await db.drop_table(guild)

async def main():
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    async with WarBot() as bot:
        await bot.start(token=bot.config.token)


asyncio.run(main())