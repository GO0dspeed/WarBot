import discord
from config.config import Config
from discord.ext import commands
from collections import Counter
import pandas as pd
import dataframe_image
from tinydb import TinyDB, Query
import json
import operator
import io

config = Config()

class queryStats(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.action = None

    @discord.ui.button(label="Activity Stats", style=discord.ButtonStyle.green)
    async def get_activity_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Crunching the Numbers", ephemeral=True)
        self.action = "activity"
        self.stop()

    @discord.ui.button(label="Win/Loss", style=discord.ButtonStyle.red)
    async def get_win_loss(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Crunching the Numbers", ephemeral=True)
        self.action = "win_loss"
        self.stop()

    @discord.ui.button(label="Last 10 Matches", style=discord.ButtonStyle.blurple)
    async def get_last_10(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Crunching the Numbers:", ephemeral=True)
        self.action = "last_10"
        self.stop()

class statCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = TinyDB(config.db)

    def get_guild_table(self, guild_id):
        return self.db.table(str(guild_id))

    async def stats_query(self, ctx):
        guild_table = self.get_guild_table(ctx.guild.id)
        data = guild_table.all()
        df = pd.json_normalize(data)

        try:
            currentChannel = ctx.channel
        except Exception as e:
            print(e)
        
        try:
            statsView = queryStats()
            statsEmbed = discord.Embed()
            statsEmbed.add_field(name="Query some stats", value="Check Clan war Stats")
            message = await currentChannel.send(embed=statsEmbed, view=statsView)
            await statsView.wait()
        except Exception as e:
            print(e)

        if statsView.action == "activity":
            try:
                players = []

                for i in df.get("lineup", []):
                    for j in i:
                        try:
                            players.append(discord.Guild.get_member(ctx.guild, j))
                        except Exception as e:
                            print(e)
                            continue

                stats = Counter(players)
                statslist = []
                for i in stats.items():
                    statslist.append(i)
                statslist.sort(key=operator.itemgetter(1))
                try:
                    table = pd.DataFrame(statslist[::-1], columns=["Player", "Wars"], )
                    print(table)
                except Exception as e:
                    print(e)
                embed = discord.Embed(title="War Activity Stats", color=discord.Color.dark_theme(), )
                dataframe_image.export(table, "images/stats.png")
                image = discord.File("images/stats.png", filename="stats.png")
                try:
                    embed.set_image(url="attachment://stats.png")
                    await currentChannel.send(file=image, embed=embed)
                    await message.delete()
                except Exception as e:
                    print(e)
            except Exception as e:
                print(e)

        elif statsView.action == "win_loss":
            record = df.get(["date", "time", "opponent", "result"])

            try:   
                embed = discord.Embed(title="War Activity Stats", color=discord.Color.dark_theme())
                dataframe_image.export(record['result'].value_counts().to_frame(), "images/stats.png")
                image = discord.File("images/stats.png", filename="stats.png")
                try:
                    embed.set_image(url="attachment://stats.png")
                    await currentChannel.send(embed=embed, file=image)
                    await message.delete()
                except Exception as e:
                    print(e)
            except Exception as e:
                print(e)

        elif statsView.action == "last_10":
            record = df.get(["date", "time", "opponent", "result"])

            try:
                embed = discord.Embed(title="War Activity Stats", color=discord.Color.dark_theme())
                dataframe_image.export(record.tail(10), "images/stats.png")
                image = discord.File("images/stats.png", filename="stats.png")
                try:
                    embed.set_image(url="attachment://stats.png")
                    await currentChannel.send(embed=embed, file=image)
                    await message.delete()
                except Exception as e:
                    print(e)
            except Exception as e:
                print(e)

    @discord.app_commands.command(name="stats")
    async def stats(self, ctx):
        print("Querying War Stats")
        await self.stats_query(ctx)

async def setup(bot):
    await bot.add_cog(statCog(bot))
