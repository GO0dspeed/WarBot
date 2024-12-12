import discord
from config.config import Config
from discord.ext import commands
from tinydb import TinyDB

config = Config()

class configButtons(discord.ui.Modal, title="Configuration Settings"):
    announcement_channel = discord.ui.TextInput(label="Channel ID forannouncements", required=True, placeholder="1099707011140065694")
    reaction_emoji = discord.ui.TextInput(label="The reaction emoji", required=True, placeholder="<:greenup:1099707265910575154>")
    role = discord.ui.TextInput(label="The role ID to ping", required=False, placeholder="979851289703850705")

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("Configuration Saved: ", ephemeral=True)

class Configure(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = TinyDB(config.db)  

    def get_guild_table(self, guild_id):
        return self.db.table(str(guild_id))  

    @discord.app_commands.command(name="configure")
    async def configure(self, ctx):
        try:
            guild_id = ctx.guild.id
            table = self.get_guild_table(guild_id)
        except Exception as e:
            print(f"Error in getting DB: {e}")
        try:
            modal = configButtons()
            await ctx.response.send_modal(modal)
            await modal.wait()
        except Exception as e:
            print(f"An error occurred...{e}")
            return
        
        try:
            table.insert({"configuration": {"announcement_channel": modal.announcement_channel.value, "reaction_emoji": modal.reaction_emoji.value, "role": modal.role.value}})
        except Exception as e:
            print(f"An error occurred updating the table: {e}")

async def setup(bot):
    await bot.add_cog(Configure(bot))