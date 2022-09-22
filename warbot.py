import asyncio
from discord.ext import commands
from discord.utils import get
import discord


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command()
async def war(ctx, opponent, date, time, team_size):
    channel = bot.get_channel(1022198665806356510) # customize this value to the channel where you want messages to appear
    emoji = '<:greenup:1022253759360929952>'
    mess = await ctx.send(f"Starting a War against {opponent} on {date} at {time} EST. React with {emoji} if you can participate")
    await mess.add_reaction(emoji)
    # def check(reaction, user):
    #     return reaction.message == mess and str(reaction.emoji) == emoji and user != bot.user
    while True:
        msg = await ctx.fetch_message(mess.id)
        reactions = msg.reactions
        for react in reactions:
            team = [user async for user in react.users() if user != bot.user]
        if len(team) == team_size:
            break
        asyncio.sleep(10)

    output = ""
    output += f"Creating a lineup for the war against {opponent} on {date} at {time} EST...\n"
    c = 1
    for player in team:
        output += "{}. <@!{}>\n".format(c, player.id)
        c += 1
            
    await channel.send(output)

bot.run(***REMOVED***) # Bot Token