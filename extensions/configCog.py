import discord
from config.config import Config
from discord.ext import command
from tinydb import TinyDB

class configButtons(discord.ui.Modal, title="Configuration Settings"):
    announcement_channel = discord.ui.TextInput(label="The channel ID for war announcements", required=True, placeholder="1099707011140065694")
    reaction_emoji = discord.ui.TextInput(label="The reaction emoji you want to use to sign up for a War", required=True, placeholder="<:greenup:1099707265910575154>")
    role = discord.ui.TextInput(label="The role ID for you clan to ping. If empty the bot will ping the everyone role", required=False, placeholder="979851289703850705")

    
