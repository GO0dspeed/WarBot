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
        discord.SelectOption(label="Foxhunt"),
        discord.SelectOption(label="Enowapi"),
        discord.SelectOption(label="Fish Hook"),
        discord.SelectOption(label="Chain Reaction"),
        discord.SelectOption(label="After Hours"),
        discord.SelectOption(label="Liberation"),
        discord.SelectOption(label="Last Bastion"),
    ])
    async def record_maps(self, interaction: discord.Interaction, select: discord.ui.Select):
        await interaction.response.send_message("Recording maps", ephemeral=True)
        self.maps = select.values
        self.stop()

class warButtons(discord.ui.Modal, title="Pre War Questionnaire"):
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
    
    def get_guild_table(self, guild_id):
        return self.db.table(str(guild_id))

    def get_current_lineup(self, guild_id, payload: discord.RawReactionActionEvent):
        search = Query()
        table = self.get_guild_table(guild_id)
        if payload.user_id != int(self.bot.user.id):
            team = table.search((search.message_id == payload.message_id))[0]["lineup"]
            return team
        
    async def post_match_survey(self, guild_id, message: discord.Message):
        resultview = RecordResult()
        mapview = RecordMaps()
        resultembed = discord.Embed()
        resultembed.add_field(name="Record Win/Loss", value="Record Win Or Loss")
        await message.edit(embed=resultembed, view=resultview)
        await resultview.wait()
        search = Query()
        table = self.get_guild_table(guild_id)
        match = table.search((search.message_id == message.id))
        if resultview.value == "Cancelled":
            table.remove((search.message_id == message.id))
            return
        elif resultview.value == "Win":
            match[0]["result"] = "win"
        else:
            match[0]["result"] = "loss"
        table.update({"result": match[0]["result"]}, (search.message_id == message.id))

        mapembed = discord.Embed()
        mapembed.add_field(name="Map Selection", value="Select which maps were played (3 or 5)")
        await message.edit(embed=mapembed, view=mapview)
        await mapview.wait()
        
        if len(mapview.maps) == len(match[0]["best of"]):
            match[0]["maps"] = mapview.maps
            table.update({"maps": match[0]["maps"]}, (search.message_id == message.id))

    async def process_reaction(self, guild_id, payload: discord.RawReactionActionEvent, r_type=None):
        print("processing reaction")
        search = Query()
        table = self.get_guild_table(guild_id)
        channel = self.bot.get_channel(config.announcement_channel)
        if str(payload.emoji) == self.reaction_emoji:
            print("entering reaction loop")
            if r_type == "add":
                if payload.user_id != int(self.bot.user.id):
                    print("not the bot")
                    if payload.user_id not in table.search((search.message_id == payload.message_id))[0]["team"]:
                        print(f"Adding {payload.user_id} to the team")
                        try:
                            team = table.search((search.message_id == payload.message_id))
                            team[0]["team"].append(payload.user_id)
                            table.update({"team": team[0]["team"]}, (search.message_id == payload.message_id))
                        except Exception as e:
                            print(e)
            elif r_type == "remove":
                if payload.user_id in table.search((search.message_id == payload.message_id))[0]["team"]:
                    team = table.search((search.message_id == payload.message_id))
                    team[0]["team"].remove(payload.user_id)
                    table.update({"team": team[0]["team"]}, (search.message_id == payload.message_id))
        elif str(payload.emoji) == self.kill_emoji:
            print("deleting the messages")
            try:
                msg = await channel.fetch_message(payload.message_id)
                tag = await channel.fetch_message(table.search((search.message_id == payload.message_id))[0]["tag"])
                await self.post_match_survey(guild_id, msg)
                msg = await channel.fetch_message(payload.message_id)
                await msg.delete()
                await tag.delete()
            except Exception as e:
                print(e)

    async def update_roster_and_post(self, guild_id, payload):
        war = Query()
        table = self.get_guild_table(guild_id)
        channel = self.bot.get_channel(config.announcement_channel)
        if table.search((war.message_id == payload.message_id)):
            print("updating the embed")
            match = table.search((war.message_id == payload.message_id))[0]
            match["lineup"] = match["team"][0:int(match["team_size"])]
            match["backups"] = match["team"][int(match["team_size"])::]
            try:
                table.update({"lineup": match["lineup"]}, (war.message_id == payload.message_id))
                table.update({"backups": match["backups"]}, (war.message_id == payload.message_id))
            except Exception as e:
                print(e)
            embed1 = discord.Embed(title=f"War Signup vs {match['opponent']}", color=discord.Color.red())
            embed1.add_field(name="Date: ", value=match['date'], inline=False)
            embed1.add_field(name=f"Time: ", value=f"{match['time']} EST", inline=False)
            embed1.add_field(name="Team size: ", value=match["team_size"], inline=False)
            embed1.add_field(name="Best Of: ", value=match["best of"], inline=False)
            embed1.add_field(name="Lineup", value=f'{self.newline.join(f"<@!{player}>" for player in match["lineup"]) if len(match["lineup"]) > 0 else "None"}', inline=False)
            embed1.add_field(name="Backups", value=f'{self.newline.join(f"<@!{player}>" for player in match["backups"]) if len(match["backups"]) > 0 else "None"}', inline=False)
            message = await channel.fetch_message(payload.message_id)
            await message.edit(embed=embed1)
    
    async def dm_added_player(self, user):
        await user.send("You have been added to the lineup")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        guild_id = payload.guild_id
        await self.process_reaction(guild_id, payload, r_type="add")
        await self.update_roster_and_post(guild_id, payload)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        guild_id = payload.guild_id
        await self.process_reaction(guild_id, payload, r_type="remove")
        await self.update_roster_and_post(guild_id, payload)

    @discord.app_commands.command(name="war")
    async def war(self, ctx):
        guild_id = ctx.guild.id
        table = self.get_guild_table(guild_id)
        print("war was initiated")
        try:
            modal = warButtons()
            await ctx.response.send_modal(modal)
            await modal.wait()
        except Exception as e:
            print(f"An error occurred...{e}")
            return
        channel = self.bot.get_channel(config.announcement_channel)
        if self.role == "":
            self.tag = await channel.send(f"{ctx.guild.default_role}")
        else:
            self.tag = await channel.send(f"<@&{self.role}>")
        embed1 = discord.Embed(title=f"War Signup vs {modal.opponent.value}", color=discord.Color.red())
        embed1.add_field(name="Date: ", value=modal.date.value, inline=False)
        embed1.add_field(name=f"Time: ", value=f"{modal.time.value} EST", inline=False)
        embed1.add_field(name="Team size: ", value=modal.team_size.value, inline=False)
        embed1.add_field(name="Best Of: ", value=modal.best_of.value, inline=False)
        embed1.add_field(name="Lineup", value="None", inline=False)
        embed1.add_field(name="Backups", value="None", inline=False)
        self.message = await channel.send(embed=embed1)
        if self.message is not None:
            await self.message.add_reaction(self.reaction_emoji)
            war_id = random.randint(0, 10000)
            try:
                print("inside the war id section")
                table.insert({"war_id": war_id, "message_id": self.message.id, "tag": self.tag.id, "opponent": modal.opponent.value, "date": modal.date.value, "time": modal.time.value, "team_size": modal.team_size.value, "best of": modal.best_of.value, "team": [], "lineup": [], "backups": []})
            except Exception as e:
                print(f"Error inserting {e}")
            print("insert completed")
            war = Query()

async def setup(bot):
    await bot.add_cog(clanWar(bot))
