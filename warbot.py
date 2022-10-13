import discord
from discord.ext import commands
from discord import Intents
import logging
from config.config import Config
import asyncio

config = Config()
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(intents=intents, command_prefix = "!")

async def main():
    async with bot:
        await bot.load_extension("extensions.warCog")
        await bot.start(token=config.token)


asyncio.run(main())