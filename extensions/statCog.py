import discord
from discord.ext import commands
from discord.ext import tasks
from config.config import Config
from tinydb import TinyDB, Query

class statCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = TinyDB("../data/db.json")

    @commands.command()
    async def stats(self, ctx):
        