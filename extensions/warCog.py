import discord
from discord.ext import commands
from discord.ext import tasks
from config.config import Config
from tinydb import TinyDB, Query
import random

config = Config()

class RecordResult(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label="Record Win", style=discord.ButtonStyle.green)
    async def record_win(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Recording Win", ephemeral=True)
        self.value = "Win"
        self.stop()

    @discord.ui.button(label="Record Loss", style=discord.ButtonStyle.red)
    async def record_loss(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Recording Loss", ephemeral=True)
        self.value = "Loss"
        self.stop()

    @discord.ui.button(label="Cancelled", style=discord.ButtonStyle.grey)
    async def record_cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Recording Cancellation", ephemeral=True)
        self.value = "Cancelled"
        self.stop()

class RecordMaps(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.maps = []

    @discord.ui.select(placeholder="Maps", min_values=3, max_values=5, options=[
        discord.SelectOption(label="Desert Glory"),
        discord.SelectOption(label="Sandstorm"),
        discord.SelectOption(label="Abandoned"),
        discord.SelectOption(label="Bitter Jungle"),
        discord.SelectOption(label="Requiem"),
        discord.SelectOption(label="Blizzard"),
        discord.SelectOption(label="Guidance"),
        discord.SelectOption(label="Sujo"),
        discord.SelectOption(label="Vigilance"),
        discord.SelectOption(label="The Mixer"),
        discord.SelectOption(label="Rats Nest"),
        discord.SelectOption(label="Night Stalker"),
        discord.SelectOption(label="Death Trap"),
        discord.SelectOption(label="Blood Lake"),
        discord.SelectOption(label="Shadow Falls"),
        discord.SelectOption(label="Crossroads"),
    ])
    async def record_maps(self, interaction: discord.Interaction, select: discord.ui.Select):
        await interaction.response.send_message("Recording maps", ephemeral=True)
        self.maps = select.values
        self.stop()

class warButtons(discord.ui.Modal, title="Pre War Questionairre"):
    opponent = discord.ui.TextInput(label="opponent", placeholder="Type who the opponent is")
    date = discord.ui.TextInput(label="date", placeholder="Date of the war")
    time = discord.ui.TextInput(label="time", placeholder="Time of the war (EST)")
    team_size = discord.ui.TextInput(label="team size", placeholder="Number of players IE: 8")
    best_of = discord.ui.TextInput(label="best of", placeholder="Best of (3 or 5)")

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("War details recorded", ephemeral=True)
    
    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message("An Error occurred", ephemeral=True)

        print(f"{error.__traceback__}")

class clanWar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message = None
        self.tag = None
        self.db = TinyDB(config.db)
        self.match = {}
        self.newline = "\n"
        self.none = "None"
        self.announcement_channel = None
        self.reaction_emoji = config.reaction_emoji
        self.kill_emoji = config.kill_emoji
        self.role = config.role

    def get_current_lineup(self, payload: discord.RawReactionActionEvent):
        search = Query()
        if payload.user_id != int(self.bot.user.id):
            team = self.db.search(search.message_id == payload.message_id)[0]["lineup"]
            return team
        
    async def post_match_survey(self, message: discord.Message):
        resultview = RecordResult()
        mapview = RecordMaps()
        resultembed = discord.Embed()
        resultembed.add_field(name="Record Win/Loss", value="Record Win Or Loss")
        await message.edit(embed=resultembed, view=resultview)
        await resultview.wait()
        if resultview.value == "Cancelled":
            search = Query()
            self.db.remove(search.message_id == message.id)
            return
        elif resultview.value == "Win":
            search = Query()
            match = self.db.search(search.message_id == message.id)
            match[0]["result"] = "win"
            self.db.update({"result": match[0]["result"]}, search.message_id == message.id)
        else:
            search = Query()
            match = self.db.search(search.message_id == message.id)
            match[0]["result"] = "loss"
            self.db.update({"result": match[0]["result"]}, search.message_id == message.id)
        mapembed = discord.Embed()
        mapembed.add_field(name="Map Selection", value="Select which maps were played (3 or 5)")
        await message.edit(embed=mapembed, view=mapview)
        await mapview.wait()
        search = Query()
        match = self.db.search(search.message_id == message.id)
        if len(mapview.maps) == len(match[0]["best of"]):
            match[0]["maps"] = mapview.maps
            self.db.update({"maps": match[0]["maps"]}, search.message_id == message.id)
            return

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
                # Add in the logic to do a post-match survey in the embed
                await self.post_match_survey(msg)
                msg = await channel.fetch_message(payload.message_id) # need to do this twice as for some reason passing to the function stops us from deleting the original embed
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

    async def dm_added_player(self, original_lineup, payload: discord.RawReactionActionEvent):
        search = Query()
        match = self.db.search(search.message_id == payload.message_id)[0]
        user = self.bot.get_user(match['team'][int(match['team_size'])-1])
        print(user.id)
        print(original_lineup)
        print(user.id in original_lineup)
        if payload.user_id != self.bot.user.id:
            if user.id not in original_lineup:
                print(f"DM'ing new addition to the lineup: {user}")
                await user.send(f"You have been added to the lineup for {match['opponent']} at {match['date']} : {match['time']} EST")
                
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
        try:
            original_lineup = self.get_current_lineup(payload)
        except Exception as e:
            print(f"Issue with gettng lineup: {e}")
        await self.process_reaction(payload, "remove")
        try:
            await self.update_roster_and_post(payload)
            await self.dm_added_player(original_lineup, payload)
        except Exception as e:
            print(e)
            pass

    @discord.app_commands.command(name="war")
    async def war(self, interaction: discord.Interaction):
        """
        Send a message and create a lineup for a war.
        """
        print("starting a war")
        try:
            self.announcement_channel = self.bot.get_channel(config.announcement_channel)
        except Exception as e:
            print(e)
        try:
            pre_survey = warButtons()
            await interaction.response.send_modal(pre_survey)
            await pre_survey.wait()
        except Exception as e:
            print(f"Failed to send modal {e}")
        match = self.match[f"{pre_survey.opponent}-{random.getrandbits(10)}"] = {}
        match["team"] = []
        match["lineup"] = []
        match["backups"] = []
        match["team_size"] = str(pre_survey.team_size)
        match["opponent"] = str(pre_survey.opponent)
        match["date"] = str(pre_survey.date)
        match["time"] = str(pre_survey.time)
        match["result"] = None
        match["maps"] = []
        match["best of"] = str(pre_survey.best_of)
        print(f"Announcements will go to {self.announcement_channel}")      
        embed = discord.Embed(title=f"War Signup vs {pre_survey.opponent}", color=discord.Color.red())
        embed.add_field(name="Date: ", value=f"{pre_survey.date}", inline=False)
        embed.add_field(name="Time: ", value=f"{pre_survey.time} EST", inline=False)
        embed.add_field(name="Desired Team Size: ", value=f"{pre_survey.team_size} v {pre_survey.team_size}", inline=False)
        embed.add_field(name="Best Of", value=f"Best Of {pre_survey.best_of}", inline=False)
        embed.add_field(name="How to sign up: ", value=f"React with {self.reaction_emoji} if you can participate", inline=False)
        if self.role == "":
            self.tag = await self.announcement_channel.send(f"{commands.context.Context.guild.default_role}")
        else:
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
