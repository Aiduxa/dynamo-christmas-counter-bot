from discord.ext.commands import Cog, Bot
from discord.app_commands import command, describe

from discord import Interaction, TextChannel, Embed, Message
from requests import get, Response

from utils import serverDatabaseHandler, Default, Color
from json import loads

from ast import literal_eval

class Commands(Cog):

    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot


    # Sets the countdown channel
    @describe(channel="The channel you want countdown to take part in.")
    @command(name="set_countdown_channel", description="Configure Dynamo's countdown channel in your server.")
    async def set_countdown_channel_command(self, inter: Interaction, channel: TextChannel):

        """
        
        Permission check has to be added - check if the user running the command has manage_guild permissions or is owner

        Check if bot has manage_messages, send_messages, use_application_commands
        
        
        """

        await inter.response.defer(ephemeral=True)

        serverDH: serverDatabaseHandler = serverDatabaseHandler(self.bot.POOL)

        await serverDH.get(inter.guild.id)

        await serverDH.update(inter.guild.id, "christmas_countdown_channel_id", channel.id)

        msg: Message = await channel.send("This message will be updated. Stay tuned.")

        await msg.pin(reason="Dynamo's daily counter until christmas")

        await serverDH.update(inter.guild.id, "christmas_countdown_message_id", msg.id)

        embed: Embed = Embed(
            title="✅ Channel has been successfully set!",
            description=f"Christmas countdown has been set to:\n- Channel: {channel.mention} ``(id: {channel.id})``\n- Message: {msg.jump_url}",
            color=Color.GREEN
        )
        embed.set_footer(text=Default.FOOTER, icon_url=self.bot.user.avatar.url)

        await inter.edit_original_response(embed=embed)

    # Returns a joke
    @command(name="joke", description="Dynamo tells you a christmas themed joke.")
    async def joke_command(self, inter: Interaction):
        
        raw_joke: Response = get("https://christmascountdown.live/api/joke")

        joke: dict = literal_eval(str(raw_joke.text).replace("\\", "").replace('’', "").strip('"'))

        embed: Embed = Embed(
            title="🎅 Let me tell you a joke...",
            description=f"## {joke['question']}\n{joke['answer']}",
            color=Color.GREEN
        )
        embed.set_footer(text=Default.FOOTER, icon_url=self.bot.user.avatar.url)

        await inter.response.send_message(embed=embed)

async def setup(bot: Bot):
    await bot.add_cog(Commands(bot))