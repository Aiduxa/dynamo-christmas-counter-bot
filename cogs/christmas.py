from discord.ext.commands import Cog, Bot
from discord.app_commands import command, describe, guild_only, AppCommandError, MissingPermissions
from discord.app_commands.checks import has_permissions
from discord.utils import format_dt
from discord import Interaction, TextChannel, Embed, Message, Permissions
from requests import get, Response

from utils import serverDatabaseHandler, Default, Color, Server, ChristmasTriviaJson, userDatabaseHandler, User, TriviaView
from time import time
from datetime import datetime
from asyncio import sleep
from random import random

from ast import literal_eval

class Christmas(Cog):

    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot

    # Sets the countdown channel
    @describe(channel="The channel you want countdown to take part in.")
    @has_permissions(manage_guild=True)
    @guild_only()
    @command(name="set_countdown_channel", description="Configure Dynamo's countdown channel in your server.")
    async def set_countdown_channel_command(self, inter: Interaction, channel: TextChannel) -> None:

        await inter.response.defer(ephemeral=True)

        channel_permissions: Permissions = channel.permissions_for(inter.guild.get_member(self.bot.user.id))

        if not channel_permissions.send_messages:

            embed = Embed(
                title="❌ Error",
                description=f"- I do not have enough permissions in {channel.mention}. I need ``Send messages`` permissions.",
                color=Color.RED
            )
            embed.set_footer(text=Default.FOOTER)

            await inter.edit_original_response(embed=embed)

            return

        serverDH: serverDatabaseHandler = serverDatabaseHandler(self.bot.POOL)

        # Gets the server data from the database, we don't use it, so we use this as a check. If it doesn't exist in the database it will create it
        await serverDH.get(inter.guild.id)

        await serverDH.update(inter.guild.id, "christmas_countdown_channel_id", channel.id)

        msg: Message = await channel.send("This message will be updated. Stay tuned.")
        if channel_permissions.manage_messages:
            await msg.pin(reason="Dynamo's daily counter until christmas")

        await serverDH.update(inter.guild.id, "christmas_countdown_message_id", msg.id)

        embed: Embed = Embed(
            title="✅ Channel has been successfully set!",
            description=f"Christmas countdown has been set to:\n- Channel: {channel.mention} ``(id: {channel.id})``\n- Message: {msg.jump_url}",
            color=Color.GREEN
        )
        embed.set_footer(text=Default.FOOTER, icon_url=self.bot.user.avatar.url)

        await inter.edit_original_response(embed=embed)

    @set_countdown_channel_command.error
    async def on_set_countdown_channel_command_error(self, inter: Interaction, error: AppCommandError):
        if isinstance(error, MissingPermissions):
            await inter.response.send_message("You're missing ``Manage server`` permission. ❌", ephemeral=True)

    # Sets christmas countdown enabled status
    @describe(status="True means enabled, otherwise False means disabled.")
    @has_permissions(manage_guild=True)
    @guild_only()
    @command(name="enable_christmas_countdown", description="Configure Dynamo's countdown status.")
    async def christmas_countdown_enabled_command(self, inter: Interaction, status: bool) -> None:

        await inter.response.defer(ephemeral=True)

        serverDH: serverDatabaseHandler = serverDatabaseHandler(self.bot.POOL)

        # Gets the server data from the database, we don't use it, so we use this as a check. If it doesn't exist in the database it will create it
        await serverDH.get(inter.guild.id)

        await serverDH.update(inter.guild.id, "christmas_countdown_enabled", status)

        embed: Embed = Embed(
            title="✅ Christmas countdown has been successfully updated!",
            description=f"- Countdown has been ``{'Enabled' if status else 'Disabled'}``.",
            color=Color.GREEN
        )
        embed.set_footer(text=Default.FOOTER, icon_url=self.bot.user.avatar.url)

        await inter.edit_original_response(embed=embed)

    @christmas_countdown_enabled_command.error
    async def christmas_countdown_enabled_command_error(self, inter: Interaction, error: AppCommandError):
        if isinstance(error, MissingPermissions):
            await inter.response.send_message("You're missing ``Manage server`` permission. ❌", ephemeral=True)

    # Returns a joke
    @command(name="joke", description="Dynamo tells you a christmas themed joke.")
    @guild_only()
    async def joke_command(self, inter: Interaction) -> None:
        
        raw_joke: Response = get("https://christmascountdown.live/api/joke")

        joke: dict = literal_eval(str(raw_joke.text).replace("\\", "").replace('’', "").strip('"'))

        embed: Embed = Embed(
            title="🎅 Let me tell you a joke...",
            description=f"## {joke['question']}\n{joke['answer']}",
            color=Color.GREEN
        )
        embed.set_footer(text=Default.FOOTER, icon_url=self.bot.user.avatar.url)

        await inter.response.send_message(embed=embed)

    
    @command(name="trivia", description="Christmas themed trivia")
    @guild_only()
    async def trivia_command(self, inter: Interaction):

        await inter.response.defer()

        XmasTrivia: ChristmasTriviaJson = ChristmasTriviaJson()

        question: dict = XmasTrivia.get_random_question()
        points: dict = XmasTrivia.get_points()[question["difficulty"]]

        trivia_start: float = time() 
        trivia_ends_in: float = datetime.fromtimestamp(trivia_start + 30.0)

        embed: Embed = Embed(
            title="🎅 Christmas trivia",
            description=f"You can get ``{points}`` points for answering this question\n# Q: {question['question']}\nAnswer: {' '.join('`{}`'.format('-' * len(word)) for word in str(question['answer']).split(' '))}\n\n- Trivia ends {format_dt(trivia_ends_in, 'R')}",
            color=Color.RED
        )

        trivia_id = random()
        self.bot.trivia_status.update({trivia_id : False})

        await inter.edit_original_response(embed=embed, view=TriviaView(self.bot, question, points, trivia_id))

        await sleep(30.0)

        if not self.bot.trivia_status[trivia_id]:
            
            embed: Embed = Embed(
                title="🎅 Christmas trivia",
                description="Noone answered in time... ❌",
                color=Color.RED
            )
            embed.set_footer(text=Default.FOOTER)
            await inter.edit_original_response(embed=embed, view=None)
        
        del self.bot.trivia_status[trivia_id]

    @command(name="trivia_leaderboard", description="Shows you leaderboard of Dynamo's christmas themed trivia globally")
    async def trivia_leaderboard_command(self, inter: Interaction):

        await inter.response.defer()

        userDH: userDatabaseHandler = userDatabaseHandler(self.bot.POOL)

        await userDH.get(inter.user.id)

        db_leaderboard: list[User] = await userDH.get_trivia_leaderboard()

        user: User = await userDH.get_trivia_ranking(inter.user.id)

        leaderboard: str = f"**You're at ``#{user.trivia_ranking}`` with ``{'{:,}'.format(user.trivia_points)}`` points**\n# {'🟩🟥' * 6}\n" 

        medals = ['🥇', '🥈', '🥉']

        for i in range(0, min(11, len(db_leaderboard))):
            user_db = db_leaderboard[i]

            user_discord = await self.bot.fetch_user(user_db.id)

            leaderboard += f"- {medals[i] if i <= 3 else ''} ``#{user_db.trivia_ranking}`` | {user_discord.display_name} with ``{'{:,}'.format(user_db.trivia_points)}`` points.\n"

        embed: Embed = Embed(
            title="🎅 Christmas trivia leaderboard",
            description=leaderboard,
            color=Default.COLOR
        )
        embed.set_footer(
            text=Default.FOOTER
        )

        await inter.edit_original_response(embed=embed)

async def setup(bot: Bot):
    await bot.add_cog(Christmas(bot))
