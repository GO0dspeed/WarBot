import discord
from config.config import Config
from discord.ext import commands
from tinydb import TinyDB
from collections import Counter
import pandas as pd
import pdfkit
import json
import operator

config = Config()

class statCog(commands.Cog):
    def __init__(self, bot):
        self.db = TinyDB(config.db)

    @commands.command()
    async def warstats(self, ctx):
        print("Querying War Stats")

        players = []

        with open(config.db, 'r',) as fp:
            data = json.load(fp)
        
        df = pd.json_normalize(data["_default"].values())
        
        try:
            currentChannel = ctx.channel
        except Exception as e:
            print(e)

        for i in df.get("lineup"):
            for j in i:
                try:
                    players.append(discord.Guild.get_member(ctx.guild, j))
                except Exception as e:
                    print(e)
                    continue
        
        stats = Counter(players)
        statslist = []
        for i in stats.items():
            statslist.append(i)
        statslist.sort(key=operator.itemgetter(1))
        try:
            table = pd.DataFrame(statslist[::-1], columns=["Player", "Wars"], )
            print(table)
        except Exception as e:
            print(e)
        embed = discord.Embed(title="War Activity Stats", color=discord.Color.dark_theme())
        image = discord.File(pdfkit.from_string(table.to_html()), filename="stats.pdf")
        try:
            embed.set_image(url="attachment://stats.pdf")
            await currentChannel.send(embed=embed, file=image)
        except Exception as e:
            print(e)

async def setup(bot):
    await bot.add_cog(statCog(bot))
        
