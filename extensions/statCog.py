import discord
from discord.ext import commands
from tinydb import TinyDB
from collections import Counter
import tabulate
import operator

class statCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = TinyDB("data/db.json")

    @commands.command()
    async def stats(self, ctx):
        print("Querying War Stats")
        players = []
        try:
            currentChannel = ctx.channel
        except Exception as e:
            print(e)

        for i in self.db.all():
            for j in i['lineup']:
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
            table = tabulate.tabulate(statslist[::-1], headers=["Player", "Wars"])
            print(table)
        except Exception as e:
            print(e)
        embed = discord.Embed(title="War Activity Stats", color=discord.Color.dark_theme())
        try:
            embed.add_field(name="Table", value=f"```{table}```")
            await currentChannel.send(embed=embed)
        except Exception as e:
            print(e)

async def setup(bot):
    await bot.add_cog(statCog(bot))
        