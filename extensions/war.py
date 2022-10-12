import discord
from discord.ext import commands
from config.config import Config

class War(commands.Cog):
    def __init__(self, opponent, date, time, team_size, bot):
        super().__init__()
        self.opponent = opponent
        self.date = date
        self.time = time
        self.team_size = team_size
        self.bot = bot
        self.message = None
        self.tag = None
        self.team = []
        self.lineup = []
        self.backups = []
        self.newline = "\n"
        self.none = "None"
        self.announcement_channel = Config.announcement_channel
        self.reaction_emoji = Config.reaction_emoji
        self.kill_emoji = Config.kill_emoji
        self.role = Config.role

    async def process_reaction(self, payload: discord.RawReactionEvent, r_type=None):
        if payload.message_id == self.message.message_id:
            if payload.emoji.name == self.reaction_emoji:
                if r_type == "add":
                    if payload.user_id not in self.team:
                        self.team.append(payload.user_id)
                elif r_type == "remove":
                    if payload.user_id in self.team:
                        self.team.remove(payload.user_id)
            elif payload.emoji.name == self.kill_emoji:
                await self.message.delete()
                await self.tag.delete()
                self.message = None
                self.tag = None
            else:
                pass

    async def update_roster_and_post(self):
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
        await self.process_reaction(payload, "add")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        await self.process_reaction(payload, "remove")

    @commands.command()
    async def war(self):
        """
        Send a message and create a lineup for a war.
        """
        embed = discord.Embed(title=f"War Signup vs {self.opponent}", color=discord.Color.red())
        embed.add_field(name="Date: ", value=self.date, inline=False)
        embed.add_field(name="Time: ", value=f"{self.time} EST", inline=False)
        embed.add_field(name="Desired Team Size: ", value=f"{self.team_size} v {self.team_size}", inline=False)
        embed.add_field(name="How to sign up: ", value=f"React with {self.reaction_emoji} if you can participate", inline=False)
        self.tag = await self.announcement_channel.send(f"<@&{self.role}>")
        self.message = await self.announcement_channel.send(embed=embed)
        await self.message.add_reaction(self.reaction_emoji)
        while self.message != None:
            await self.update_roster_and_post()

def setup(bot):
    bot.add_cog(War(bot))