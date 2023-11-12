from discord.app_commands import command, describe, Command
from discord.ext.commands import Cog, Bot
from discord import Interaction, Embed

from utils import Default

class HelpCommand(Cog):

    def __init__(self, bot: Bot):
        self.bot: Bot = bot

    @command(name="help", description="Dynamo's commands")
    async def help_command(self, inter: Interaction):

        await inter.response.defer()

        commands: list[Command] = self.bot.tree.get_commands()

        command_list: str = ""

        for cmd in commands:
            command_list += f"- **``/{cmd.name}``**\n{cmd.description}\n"

        embed: Embed = Embed(
            title="Dynamo's commands",
            description=f"Currently **Dynamo** has ``{len(commands)}`` commands. \n\n{command_list}",
            color=Default.COLOR
        )
        embed.set_footer(text=Default.FOOTER)

        await inter.edit_original_response(embed=embed)

async def setup(bot: Bot):
    await bot.add_cog(HelpCommand(bot))