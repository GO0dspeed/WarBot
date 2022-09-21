import re
from discord.ext import commands
from discord.utils import get
import discord

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
NAME = re.compile(r"(.*)#(.*)")

@bot.command()
async def war(ctx, arg):
    channel = bot.get_channel(1022198665806356510)
    emoji = '<:greenup:1022253759360929952>'
    mess = await ctx.send(f"Starting a War against {arg}. React with {emoji} if you can participate")
    await mess.add_reaction(emoji)

    def check(reaction, user):
        return reaction.message == mess and str(reaction.emoji) == emoji and user != bot.user

    team = []

    while True:
        user = await bot.wait_for("reaction_add", check=check)
        team.append(user[1])
        if len(team) == 3:
            break

    output = ""
    output += f"Creating a lineup for the war against {arg}...\n"
    c = 1
    for player in team:
        output += "{}. <@!{}>\n".format(c, player.id)
        c += 1
            
    await channel.send(output)

bot.run(***REMOVED***)