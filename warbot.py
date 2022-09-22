import asyncio
from dis import disco
from discord.ext import commands
from discord.ext import tasks
from discord.utils import get
import discord


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
newline = "\n"
none = "None"

def _compare_lists(old, new):
    old_list = set(old)
    new_list = set(new)


@bot.command()
async def war(ctx, opponent, date, time, team_size):
    """Send a message to create a lineup for a war.
    """
    emoji = '<:greenup:1022253759360929952>'
    channel = bot.get_channel(1022198665806356510) # customize this value to the channel where you want messages to appear
    adjusted_team_size = int(team_size) - 1
    embed = discord.Embed(title=f"War Signup vs {opponent}", color=discord.Color.red())
    embed.add_field(name="Date: ", value=date, inline=False)
    embed.add_field(name="Time: ", value=f"{time} EST", inline=False)
    embed.add_field(name="Desired Team Size: ", value=f"{team_size} v {team_size}", inline=False)
    embed.add_field(name="How to sign up: ", value=f"React with {emoji} if you can participate", inline=False)
    mess = await channel.send(embed=embed)
    await mess.add_reaction(emoji)
    team = []

    while True:
        msg = await channel.fetch_message(mess.id)
        reactions = msg.reactions
        for react in reactions:
            users = [user.id async for user in react.users() if user != bot.user]

        for i in users:
            if i not in team:
                team.append(i)
        for i in team:
            if i not in users:
                team.remove(i)

                
        lineup = team[0:int(team_size)]
        
        backups = team[int(team_size)::]

        embed1 = discord.Embed(title=f"War Signup vs {opponent}", color=discord.Color.red())
        embed1.add_field(name="Date: ", value=date, inline=False)
        embed1.add_field(name=f"Time: ", value=f"{time} EST", inline=False)
        embed1.add_field(name=f"Desired Team Size: ", value=f"{team_size} v {team_size}", inline=False)
        embed1.add_field(name="How to sign up: ", value=f"React with {emoji} if you can participate", inline=False)
        embed1.add_field(name="Current Lineup: ", value=f'{newline.join(f"<@!{player}>" for player in lineup) if len(lineup) > 0 else "None"}', inline=False)
        embed1.add_field(name="Current Backups: ", value=f'{newline.join(f"<@!{player}>" for player in backups) if len(backups) > 0 else "None"}', inline=False)
        await mess.edit(embed = embed1)
        
        asyncio.sleep(1)
bot.run(***REMOVED***) # Bot Token