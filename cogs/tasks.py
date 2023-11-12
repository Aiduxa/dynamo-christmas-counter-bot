from discord.ext.commands import Cog, Bot
from discord.ext.tasks import loop
from discord import TextChannel, Message, Embed, Guild

from utils import serverDatabaseHandler, Server, Color, Default

from aiohttp import ClientSession
from json import loads

def create_progress_bar(percentage, length=14):
    progress = int(length * percentage / 100)
    bar = "🟦" * progress + "⬜" * (length - progress)
    return bar


class Tasks(Cog):

    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot
        self.christmas_countdown.start()
        

    @loop(hours=1)
    async def christmas_countdown(self) -> None:

        serverDH: serverDatabaseHandler = serverDatabaseHandler(self.bot.POOL)

        servers: list[Server] = await serverDH.getAll()

        for server in servers:

            # Checks if bot is still in guild, if not it deletes it from the database
            if not await self.bot.fetch_guild(server.id):
                await serverDH.delete(server.id)
                continue
            
            if not server.christmas_countdown_enabled:
                continue
                
            guild: Guild = await self.bot.fetch_guild(server.id)

            # If channel was not set, it the loop continues
            if not await guild.fetch_channel(server.christmas_countdown_channel_id):
                continue

            channel: TextChannel = await guild.fetch_channel(server.christmas_countdown_channel_id)

            # If message was deleted or some how gone, it will just send a new one.
            if not await channel.fetch_message(server.christmas_countdown_message_id):
                msg: Message = await channel.send("This will update... Stay tuned...")
                server.christmas_countdown_message_id: int = msg.id
                await serverDH.update(server.id, "christmas_countdown_message_id", msg.id)
                continue

            message: Message = await channel.fetch_message(server.christmas_countdown_message_id)

            async with ClientSession() as sesh:
                async with sesh.get("https://christmascountdown.live/api/timeleft/total") as resp:
                    # Gets the time left until christmas in dict
                    timeleft: dict = loads(str(await resp.text()))

                async with sesh.get("https://christmascountdown.live/api/percentage") as resp:
                    # Gets the percentage of time left until christmas in float
                    percentage: float = float(await resp.text())

                async with sesh.get("https://christmascountdown.live/api/is-tomorrow") as resp:
                    # Gets a bool that indicates if it's christmas eve
                    christmas_eve: bool = loads(await resp.text())

                async with sesh.get("https://christmascountdown.live/api/is-today") as resp:
                    # Gets a bool that indicates if it's christmas
                    christmas: bool = loads(await resp.text())

            line: str = "🟥🟩" * 6
            time: str  = "# Merry Christmas! 🎅🎄"

            if not christmas:
                countdown: str = ""

                for unit in ["day", "hour", "minute", "second"]:
                    u: int = timeleft.get(unit + "s")
                
                    if not u: break

                    countdown += f"`{u}` **{unit}{'s' if u > 1 else ''}** "

                time = " ".join(["### 🕒", countdown])

                if christmas_eve:
                    time = f"# Merry Christmas Eve! ⭐🎄\n{time}"

            percentage_progress: str = f"- {round(percentage)}% **/ 100%**"

            progress: str = "\n".join([f"### ⭐ Progress", percentage_progress, create_progress_bar(percentage)])

            description: str = "\n".join(["## ", line, time, progress, "## ", line])

            # Big ass embed
            embed: Embed = Embed(
                title="🎅 Countdown until christmas...",
                description=description,
                color=Color.GREEN
            )
            embed.set_footer(text=Default.FOOTER, icon_url=self.bot.user.avatar.url)

            await message.edit(content=None, embed=embed)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Tasks(bot))