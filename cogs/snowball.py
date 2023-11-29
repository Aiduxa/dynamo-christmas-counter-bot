from discord.ext.commands import Cog, Bot
from discord.app_commands import command, describe, Group, guild_only

from discord import Interaction, Member, Embed

from utils import userDatabaseHandler, User, Color
from time import time
from asyncio import sleep

class SnowballCog(Cog):

    def __init__(self, bot: Bot):
        self.bot: Bot = bot
        self.thrown_snowballs: dict = {}
    
    snowball: Group = Group(name="snowball", description="Snowball throwing mini-game") 

    @snowball.command(name="throw")
    async def throw_command(self, inter: Interaction, member: Member) -> None:

        await inter.response.defer()

        if member.bot:
            await inter.edit_original_response(content="Why would you want to throw a snowball at a robot, what's the point...")
            return

        if member.id == inter.user.id:
            await inter.edit_original_response(content="You cannot throw a snowball at yourself...")
            return

        if not self.thrown_snowballs.get(member.id):
           self.thrown_snowballs.update({member.id: {inter.user.id: time()}}) 
        else:
            if not self.thrown_snowballs[member.id].get(inter.user.id):
                self.thrown_snowballs[member.id].update({inter.user.id: time()})
            else:
                await inter.edit_original_response(content=f"❄ You have already thrown a snowball at {member.mention}, please wait a bit before throwing another one")
                return



        await inter.edit_original_response(content=f"❄ Throwing a snowball at {member.mention}\n*You have 30 seconds to dodge the snowball! (`/snowball dodge`)*")

        await sleep(30.0)

        userDH: userDatabaseHandler = userDatabaseHandler(self.bot.POOL)
        user: User = await userDH.get(inter.user.id)
        member_db: User = await userDH.get(member.id)
        if not member_db:
            await userDH.create(member.id)
            member_db = await userDH.get(member.id)

        await userDH.update(inter.user.id, "snowball_throws", user.snowball_throws + 1)

        if self.thrown_snowballs.get(member_db.id):
            await userDH.update(inter.user.id, "snowball_hits", user.snowball_hits + 1)
            await userDH.update(member.id, "snowball_struck", member_db.snowball_struck + 1)
            await inter.edit_original_response(content=f"⛄ You threw a snowball at {member.mention}! ✅")
            del self.thrown_snowballs[member.id][inter.user.id]
            return
        await inter.edit_original_response(content="😞 The snowball missed. ❌")
        
    @snowball.command(name="dodge")
    async def dodge_command(self, inter: Interaction) -> None:

        await inter.response.defer()

        if not self.thrown_snowballs.get(inter.user.id):
            await inter.edit_original_response(content=f"🤨 Nobody threw a snowball at you, why are you dodging?")
            return
        
        thrown_snowballs: dict = self.thrown_snowballs[inter.user.id]
        del self.thrown_snowballs[inter.user.id]

        userDH: userDatabaseHandler = userDatabaseHandler(self.bot.POOL)

        user: User = await userDH.get(inter.user.id)
        if not user:
            await userDH.create(inter.user.id)
            user = await userDH.get(inter.user.id)

        await userDH.update(inter.user.id, "snowball_dodges", user.snowball_dodges + len(thrown_snowballs))

        await inter.edit_original_response(content=f"😄 You dodged ``{len(thrown_snowballs)}`` snowballs")


    @snowball.command(name="stats")
    async def snowball_stats_command(self, inter: Interaction) -> None:
        
        await inter.response.defer()

        userDH: userDatabaseHandler = userDatabaseHandler(self.bot.POOL)
        user: User = await userDH.get(inter.user.id)

        embed: Embed = Embed(
            title=":snowflake: Snowball mini-game",
            description=f"You threw {'`{:,}`'.format(user.snowball_throws)} snowballs and you've successfully hit {'`{:,}`'.format(user.snowball_hits)} times.\n\nYou dodged {'`{:,}`'.format(user.snowball_dodges)} snowballs out of {'`{:,}`'.format(user.snowball_struck + user.snowball_dodges)} attempts",
            color=Color.GREEN
        )

        await inter.edit_original_response(embed=embed)

async def setup(bot: Bot):
    await bot.add_cog(SnowballCog(bot))