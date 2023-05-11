import discord
from discord.ext import commands
from discord.ext import tasks
from config.config import Config
from tinydb import TinyDB, Query
import random

config = Config()

class clanWar(commands.Cog):
    def __init__(self, bot):
        # self.opponent = ""
        # self.date = ""
        # self.time = ""
        # self.team_size = ""
        self.bot = bot
        self.message = None
        self.tag = None
        # self.team = []
        # self.lineup = []
        # self.backups = []
        self.db = TinyDB("data/db.json")
        self.match = {}
        self.newline = "\n"
        self.none = "None"
        self.announcement_channel = None
        self.reaction_emoji = config.reaction_emoji
        self.kill_emoji = config.kill_emoji
        self.role = config.role

    async def process_reaction(self, payload: discord.RawReactionActionEvent, r_type=None):
        print("processing reaction")
        search = Query()
        channel = self.bot.get_channel(config.announcement_channel)
        if str(payload.emoji) == self.reaction_emoji:
            if r_type == "add":
                if payload.user_id != int(self.bot.user.id):
                    print("not the bot")
                    if payload.user_id not in self.db.search(search.message_id == payload.message_id)[0]["team"]:
                        print(f"Adding {payload.user_id} to the team")
                        try:
                            team = self.db.search(search.message_id == payload.message_id)
                            team[0]["team"].append(payload.user_id)
                            print(team[0]["team"])
                            print(type(team))
                            self.db.update({"team": team[0]["team"]}, search.message_id == payload.message_id)
                        except Exception as e:
                            print(e)
            elif r_type == "remove":
                if payload.user_id in self.db.search(search.message_id == payload.message_id)[0]["team"]:
                    team = self.db.search(search.message_id == payload.message_id)
                    team[0]["team"].remove(payload.user_id)
                    self.db.update({"team": team[0]["team"]}, search.message_id == payload.message_id)            
        elif str(payload.emoji) == self.kill_emoji:
            print("deleting the messages")
            try:
                msg = await channel.fetch_message(payload.message_id)
                tag = await channel.fetch_message(self.db.search(search.message_id == payload.message_id)[0]["tag"])
                await msg.delete()
                await tag.delete()
            except Exception as e:
                print(e)
        else:
            pass

    async def update_roster_and_post(self, payload):
        war = Query()
        channel = self.bot.get_channel(config.announcement_channel)
        if self.db.search(war.message_id == payload.message_id):
            print("updating the embed")
            match = self.db.search(war.message_id == payload.message_id)[0]
            match["lineup"] = match["team"][0:int(match["team_size"])]
            match["backups"] = match["team"][int(match["team_size"])::]
            try:
                self.db.update({"lineup": match["lineup"]}, war.message_id == payload.message_id)
                self.db.update({"backups": match["backups"]}, war.message_id == payload.message_id)
            except Exception as e:
                print(e)
            embed1 = discord.Embed(title=f"War Signup vs {match['opponent']}", color=discord.Color.red())
            embed1.add_field(name="Date: ", value=match['date'], inline=False)
            embed1.add_field(name=f"Time: ", value=f"{match['time']} EST", inline=False)
            embed1.add_field(name=f"Desired Team Size: ", value=f"{match['team_size']} v {match['team_size']}", inline=False)
            embed1.add_field(name="How to sign up: ", value=f"React with {self.reaction_emoji} if you can participate", inline=False)
            embed1.add_field(name="Current Lineup: ", value=f'{self.newline.join(f"<@!{player}>" for player in match["lineup"]) if len(match["lineup"]) > 0 else "None"}', inline=False)
            embed1.add_field(name="Current Backups: ", value=f'{self.newline.join(f"<@!{player}>" for player in match["backups"]) if len(match["backups"]) > 0 else "None"}', inline=False)
            msg = await channel.fetch_message(payload.message_id)
            try:
                await msg.edit(embed = embed1)
            except Exception as e:
                print(e)
        else:
            pass

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        print("reaction added")
        await self.process_reaction(payload, "add")
        try:
            if str(payload.emoji) != self.kill_emoji:
                await self.update_roster_and_post(payload)
        except Exception as e:
            print(e)
            pass

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        print("reaction removed")
        await self.process_reaction(payload, "remove")
        try:
            await self.update_roster_and_post(payload)
        except Exception as e:
            print(e)
            pass

    @commands.command()
    async def war(self, ctx, opponent, date, time, team_size):
        """
        Send a message and create a lineup for a war.
        """
        # self.opponent = opponent
        # self.date = date
        # self.time = time
        # self.team_size = team_size
        print("starting a war")
        try:
            self.announcement_channel = self.bot.get_channel(config.announcement_channel)
        except Exception as e:
            print(e)
        match = self.match[f"{opponent}-{random.getrandbits(10)}"] = {}
        match["team"] = []
        match["lineup"] = []
        match["backups"] = []
        match["team_size"] = team_size
        match["opponent"] = opponent
        match["date"] = date
        match["time"] = time
        print(f"Announcements will go to {self.announcement_channel}")      
        embed = discord.Embed(title=f"War Signup vs {opponent}", color=discord.Color.red())
        embed.add_field(name="Date: ", value=f"{date}", inline=False)
        embed.add_field(name="Time: ", value=f"{time} EST", inline=False)
        embed.add_field(name="Desired Team Size: ", value=f"{team_size} v {team_size}", inline=False)
        embed.add_field(name="How to sign up: ", value=f"React with {self.reaction_emoji} if you can participate", inline=False)
        self.tag = await self.announcement_channel.send(f"<@&{self.role}>")
        match["tag"] = self.tag.id
        self.message = await self.announcement_channel.send(embed=embed)
        match["message_id"] = self.message.id
        try:
            self.db.insert(match)
        except Exception as e:
            print(e)
            print(type(match))
        await self.message.add_reaction(self.reaction_emoji)

async def setup(bot):
    await bot.add_cog(clanWar(bot))
