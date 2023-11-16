from discord.ext.commands import Cog, Bot
from discord.app_commands import command, describe, guild_only
from discord.app_commands.checks import has_permissions, bot_has_permissions
from discord.utils import format_dt
from discord import Interaction, TextChannel, Embed, Message, Permissions, InteractionMessage
from requests import get, Response

from utils import serverDatabaseHandler, Default, Color, Server, database, ChristmasTriviaJson, userDatabaseHandler, User
from time import time
from datetime import datetime
from asyncio import TimeoutError
from platform import python_version, system, release, version

from ast import literal_eval

class Commands(Cog):

    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot

    @command(name="status", description="Dynamo's current status")
    @guild_only()
    async def status_command(self, inter: Interaction):
        
        await inter.response.defer()

        serverDH: serverDatabaseHandler = serverDatabaseHandler(self.bot.POOL)

        embed: Embed = Embed(
            title="Dynamo's status",
            description=f"I'm running on **Discord.py** with Python v**{python_version()}**\n",
            color=Default.COLOR
        )
        embed.add_field(
            name="Statistics",
            value=f"{'``{:,}``'.format(len(self.bot.guilds))} servers with approximately {'``{:,}``'.format(len(self.bot.users))} members"
        )
        embed.add_field(
            name="Latency (Dynamo -> Discord)",
            value="``{:,}``**ms**".format(round(self.bot.latency * 1000, 2))
        )
        embed.add_field(
            name="Database latency",
            value="``{:,}``**ms**".format(round(await serverDH.get_db_latency() * 1000, 2))
        )

        await inter.edit_original_response(embed=embed)

async def setup(bot: Bot):
    await bot.add_cog(Commands(bot))