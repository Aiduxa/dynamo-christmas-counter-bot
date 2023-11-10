from discord.ext.commands import Cog, Bot
from discord.ext.tasks import loop
from discord import TextChannel, Message, Embed, Guild

from utils import serverDatabaseHandler, Server, Color

from aiohttp import ClientSession
from json import loads

def create_progress_bar(percentage, length=20):
    progress = int(length * percentage / 100)
    bar = "🟦" * progress + "⬜" * (length - progress)
    return bar


class Tasks(Cog):

    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot

        self.christmas_countdown.start()

    @loop(hours=5)
    async def christmas_countdown(self) -> None:

        serverDH: serverDatabaseHandler = serverDatabaseHandler(self.bot.POOL)

        servers: list[Server] = await serverDH.getAll()

        for server in servers:

            if not await self.bot.fetch_guild(server.id):
                await serverDH.delete(server.id)
                continue

            guild: Guild = await self.bot.fetch_guild(server.id)

            if not await guild.fetch_channel(server.christmas_countdown_channel_id):
                continue

            channel: TextChannel = await guild.fetch_channel(server.christmas_countdown_channel_id)

            if not await channel.fetch_message(server.christmas_countdown_message_id):
                msg: Message = await channel.send("This will update... Stay tuned...")
                server.christmas_countdown_message_id = msg.id
                await serverDH.update(server.id, "christmas_countdown_message_id", msg.id)
                continue

            messageable: Message = await channel.fetch_message(server.christmas_countdown_message_id)

            async with ClientSession() as sesh:
                async with sesh.get("https://christmascountdown.live/api/timeleft/total") as resp:

                    timeleft: dict = loads(str(await resp.text()))

                async with sesh.get("https://christmascountdown.live/api/percentage") as resp:

                    percentage: float = float(await resp.text())

                async with sesh.get("https://christmascountdown.live/api/is-tomorrow") as resp:

                    christmas_eve: bool = loads(await resp.text())

                async with sesh.get("https://christmascountdown.live/api/is-today") as resp:

                    christmas: bool = loads(await resp.text())

            embed: Embed = Embed(
                title="🎅 Countdown until christmas...",
                description=f"## 🟥🟩🟥🟩🟥🟩🟥🟩🟥🟩🟥🟩🟥🟩🟥🟩\n{'# Merry Christmas Eve! ⭐🎄' if christmas_eve else ''}{'# Merry Christmas! 🎅🎄' if christmas else ''}\n{'### ``{}``'.format(timeleft['days']) if timeleft.get('days') and not christmas else ''}{' **{}** '.format('days' if int(timeleft.get('days')) > 1 else 'day') if timeleft.get('days') and not christmas else ''}{'``{}``'.format(timeleft['minutes']) if timeleft.get('minutes') and not christmas else ''}{' **{}** '.format('minutes' if int(timeleft.get('minutes')) > 1 else 'minute') if timeleft.get('minutes') and not christmas else ''}{'``{}``'.format(timeleft['seconds']) if timeleft.get('seconds') and not christmas else ''}{' **{}** '.format('seconds' if int(timeleft.get('seconds')) > 1 else 'second') if timeleft.get('seconds') and not christmas else ''} {'until the magical {}!'.format('days' if int(timeleft.get('days')) > 1 else 'day') if not christmas else ''}\n### ⭐ Progress\n- {'**{}**'.format(round(percentage, 2)) if percentage >= 100.0 else round(percentage, 2)}%** / 100%**\n{create_progress_bar(percentage)}\n## 🟥🟩🟥🟩🟥🟩🟥🟩🟥🟩🟥🟩🟥🟩🟥🟩",
                color=Color.GREEN
            )

            await messageable.edit(content=None, embed=embed)




async def setup(bot: Bot) -> None:
    await bot.add_cog(Tasks(bot))