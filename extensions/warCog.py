import discord
from discord.ext import commands
from discord.ext import tasks
from config.config import Config

config = Config()

class clanWar(commands.Cog):
    def __init__(self, bot):
        self.opponent = ""
        self.date = ""
        self.time = ""
        self.team_size = ""
        self.bot = bot
        self.message = None
        self.tag = ""
        self.team = []
        self.lineup = []
        self.backups = []
        self.newline = "\n"
        self.none = "None"
        self.announcement_channel = None
        self.reaction_emoji = config.reaction_emoji
        self.kill_emoji = config.kill_emoji
        self.role = config.role

    async def process_reaction(self, payload: discord.RawReactionActionEvent, r_type=None):
        print("processing reaction")
        if payload.message_id == self.message.id:
            print(payload.emoji)
            print(self.reaction_emoji)
            if str(payload.emoji) == self.reaction_emoji:
                print("emojis match")
                if r_type == "add":
                    print(self.bot.user.id)
                    print(payload.user_id)
                    if payload.user_id != int(self.bot.user.id):
                        print("Not the Bot")
                        if payload.user_id not in self.team:
                            print("appending to the team")
                            self.team.append(payload.user_id)
                elif r_type == "remove":
                    if payload.user_id in self.team:
                        self.team.remove(payload.user_id)
            elif str(payload.emoji) == self.kill_emoji:
                await self.message.delete()
                await self.tag.delete()
            else:
                pass

    async def update_roster_and_post(self):
        print(self.team)
        self.lineup = self.team[0:int(self.team_size)]
        self.backups = self.team[int(self.team_size)::]

        embed1 = discord.Embed(title=f"War Signup DoX vs {self.opponent}", color=discord.Color.red())
        embed1.add_field(name="Date: ", value=self.date, inline=False)
        embed1.add_field(name=f"Time: ", value=f"{self.time} EST", inline=False)
        embed1.add_field(name=f"Desired Team Size: ", value=f"{self.team_size} v {self.team_size}", inline=False)
        embed1.add_field(name="How to sign up: ", value=f"React with {self.reaction_emoji} if you can participate", inline=False)
        embed1.add_field(name="Current Lineup: ", value=f'{self.newline.join(f"<@!{player}>" for player in self.lineup) if len(self.lineup) > 0 else "None"}', inline=False)
        embed1.add_field(name="Current Backups: ", value=f'{self.newline.join(f"<@!{player}>" for player in self.backups) if len(self.backups) > 0 else "None"}', inline=False)
        await self.message.edit(embed = embed1)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        print("reaction added")
        await self.process_reaction(payload, "add")
        try:
            await self.update_roster_and_post()
        except:
            pass

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        print("reaction removed")
        await self.process_reaction(payload, "remove")
        try:
            await self.update_roster_and_post()
        except:
            pass

    @commands.command()
    async def war(self, ctx, opponent, date, time, team_size):
        """
        Send a message and create a lineup for a war.
        """
        self.opponent = opponent
        self.date = date
        self.time = time
        self.team_size = team_size
        print("starting a war")
        try:
            self.announcement_channel = self.bot.get_channel(config.announcement_channel)
        except Exception as e:
            print(e)
        print(f"Announcements will go to {self.announcement_channel}")      
        embed = discord.Embed(title=f"War Signup vs {opponent}", color=discord.Color.red())
        embed.add_field(name="Date: ", value=f"{date}", inline=False)
        embed.add_field(name="Time: ", value=f"{time} EST", inline=False)
        embed.add_field(name="Desired Team Size: ", value=f"{team_size} v {team_size}", inline=False)
        embed.add_field(name="How to sign up: ", value=f"React with {self.reaction_emoji} if you can participate", inline=False)
        self.tag = await self.announcement_channel.send(f"<@&{self.role}>")
        self.message = await self.announcement_channel.send(embed=embed)
        await self.message.add_reaction(self.reaction_emoji)

async def setup(bot):
    await bot.add_cog(clanWar(bot))
