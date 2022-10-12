import discord
from discord.ext import commands
import logging
from config.config import Config

from warbot import war

class WarBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.command_prefix = "!"
        self.intents = discord.Intents.default()
        self.intents.message_content = True
        self.intents.reactions = True

        self.load_extension("extensions.war")
    

if __name__ == "__main__":
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    WarBot.run(token=Config.token, log_handler=handler)