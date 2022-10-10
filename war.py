import discord

class War:
    def __init__(self, message: discord.PartialMessage):
        self.message_id = message.id
        self.reactions = []
    
    def update_reactions(message)