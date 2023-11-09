from discord.ext.commands import Cog, Bot
from discord.app_commands import command, describe

from discord import Interaction, TextChannel, Embed

from utils import Server, serverDatabaseHandler, Embeds, Default

def replacevars(text: str, variables: dict) -> str:
    for variable, value in variables.items():
        text = text.replace(variable, str(value))
    return text

class Commands(Cog):

    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot


    # Sets the countdown channel
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

        msg = await channel.send("This message will be updated. Stay tuned.")

        await msg.pin(reason="Dynamo's daily counter until christmas")

        await serverDH.update(inter.guild.id, "christmas_countdown_message_id", msg.id)

        vars = {
            "%CHANNEL_MENTION%": channel.mention,
            "%CHANNEL_ID%": channel.id,
            "%MESSAGE_LINK%": msg.jump_url
        }

        embed: Embed = Embeds.set_countdown_channel_embed
        embed.description = replacevars(embed.description, vars)
        embed.set_footer(text=Default.FOOTER, icon_url=self.bot.user.avatar.url)

        await inter.edit_original_response(embed=embed)



async def setup(bot: Bot):
    await bot.add_cog(Commands(bot))