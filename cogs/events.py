from discord.ext.commands import Cog, Bot
from discord import Guild, Member

from utils import serverDatabaseHandler

class Events(Cog):

    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot

    @Cog.listener()
    async def on_guild_join(self, guild: Guild) -> None:

        serverDH: serverDatabaseHandler = serverDatabaseHandler(self.bot.POOL)

        await serverDH.create(guild.id)

    @Cog.listener()
    async def on_guild_remove(self, guild: Guild) -> None:

        serverDH: serverDatabaseHandler = serverDatabaseHandler(self.bot.POOL)

        await serverDH.delete(guild.id)

    @Cog.listener()
    async def on_user_join(self, member: Member) -> None:
        ...

    @Cog.listener()
    async def on_user_remove(self, member: Member) -> None:
        ...

async def setup(bot: Bot):
    await bot.add_cog(Events(Bot))