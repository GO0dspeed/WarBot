import re, random
from discord.ext import commands

bot = commands.Bot(command_prefix='!')
NAME = re.compile(r"(.*)#(.*)")

@bot.command()
async def team(ctx, arg="799945229"):
    message = bot.get_message("")

    # voice_channel = bot.get_channel(140920999041302528)
    # reaction_members_size = len(voice_channel.members)
    team_size = int(arg)
    team = []
    output = ""

    if team_size > 8 or team_size == 799945229:
        team_size = 8

    if team_size <= 0 or team_size <= 0:
        await ctx.send("I can't make a team without members!")
    else:
        if team_size >= 1:
            for member in reactions.members:
                    name = NAME.search(str(member))
                    if name:
                        team.append(name.group(1))
        
            if team_size < team_size:
                team = random.sample(team, team_size)
            else:
                team = random.sample(team, team_size)


            output += "Creating a random team without aaron...\n"
            c = 1
            for player in team:
                output += "{}. {}\n".format(c, player)
                c += 1
            
            await ctx.send(output)

bot.run('')