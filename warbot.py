import asyncio
from discord.ext import commands
from discord.ext import tasks
import discord


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
newline = "\n"
none = "None"

@bot.command()
async def war(ctx, opponent, date, time, team_size):
    """Send a message to create a lineup for a war.
    """
    emoji = '<:greenup:1022643911728058407>'
    kill_emoji = '⏹️'
    channel = bot.get_channel(981999185400320040) # customize this value to the channel where you want messages to appear
    adjusted_team_size = int(team_size) - 1
    embed = discord.Embed(title=f"War Signup vs {opponent}", color=discord.Color.red())
    embed.add_field(name="Date: ", value=date, inline=False)
    embed.add_field(name="Time: ", value=f"{time} EST", inline=False)
    embed.add_field(name="Desired Team Size: ", value=f"{team_size} v {team_size}", inline=False)
    embed.add_field(name="How to sign up: ", value=f"React with {emoji} if you can participate", inline=False)
    tag = await channel.send("<@979855289773850706>")
    mess = await channel.send(embed=embed)
    await mess.add_reaction(emoji)
    team = []

    while True:
        msg = await channel.fetch_message(mess.id)
        reactions = msg.reactions
        for react in reactions:
            users = [user.id async for user in react.users() if (user != bot.user and react.emoji == emoji) ]
            if react.emoji == kill_emoji:
                await tag.delete()
                await mess.delete()
                break
                
        for i in users:
            if i not in team:
                team.append(i)
        for i in team:
            if i not in users:
                team.remove(i)

                
        lineup = team[0:int(team_size)]
        
        backups = team[int(team_size)::]

        embed1 = discord.Embed(title=f"War Signup DoX vs {opponent}", color=discord.Color.red())
        embed1.add_field(name="Date: ", value=date, inline=False)
        embed1.add_field(name=f"Time: ", value=f"{time} EST", inline=False)
        embed1.add_field(name=f"Desired Team Size: ", value=f"{team_size} v {team_size}", inline=False)
        embed1.add_field(name="How to sign up: ", value=f"React with {emoji} if you can participate", inline=False)
        embed1.add_field(name="Current Lineup: ", value=f'{newline.join(f"<@!{player}>" for player in lineup) if len(lineup) > 0 else "None"}', inline=False)
        embed1.add_field(name="Current Backups: ", value=f'{newline.join(f"<@!{player}>" for player in backups) if len(backups) > 0 else "None"}', inline=False)
        await mess.edit(embed = embed1)
       
        await asyncio.sleep(2)
bot.run(***REMOVED***) # Bot Token