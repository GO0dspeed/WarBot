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

@bot.event
async def on_ready():
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} command(s).")
    print(f"Commands are {synced}")


async def main():
    async with bot:
        await bot.load_extension("extensions.warCog")
        await bot.load_extension("extensions.statCog")
        await bot.start(token=config.token)


asyncio.run(main())