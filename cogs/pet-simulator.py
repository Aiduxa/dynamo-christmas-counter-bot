from discord.ext.commands import Cog, Bot
from discord.app_commands import command

from discord import Interaction, Embed
from discord.utils import format_dt

from utils import petsDatabaseHandler, userDatabaseHandler, Pet, Color, Default, PetCreation, PetMainMenu, Variables
from random import randint

from time import time
from datetime import datetime

from utils import User

class PetSimulator(Cog):

    def __init__(self, bot: Bot):
        self.bot: Bot = bot
    
    @command(name="pet", description="Your virtual pet")
    async def pet_simulator(self, inter: Interaction):

        await inter.response.defer()

        petsDH: petsDatabaseHandler = petsDatabaseHandler(self.bot.POOL)
        userDH: userDatabaseHandler = userDatabaseHandler(self.bot.POOL)

        pet: Pet | None = await petsDH.get(inter.user.id)

        description: str = 'You don\'t own a pet. 😞\n\nTo own a pet press **"Look for a pet"** button below.'

        if pet:

            

            pet_age_days: int = int(float(time() - pet.created_at.timestamp()) / 86400)

            

            print("last_inter", int(time() - pet.last_interaction))
            if int(time() - pet.last_interaction) > 86400:
                
                if not pet.hunger == 100:
                    
                    pet.hunger = min(pet.hunger + int(float(time() - pet.last_fed) / 86400) * randint(5, 10), 100)
                    await petsDH.update(inter.user.id, "hunger", pet.hunger)
                else:
                    if pet.health > 0:
                        pet.health = min(pet.health - int(float(time() - pet.last_fed) / 86400), 0)
                        await petsDH.update(inter.user.id, "health", pet.health)
                    else:
                        
                        await petsDH.delete(inter.user.id)

            pet.last_interaction = time()

            await petsDH.update(inter.user.id, "last_interaction", pet.last_interaction)

            pet_searching: str = ''
            if pet.searching:
                
                time_left = pet.searching_till - time()
                
                if time_left > 0:

                    pet.searching_till = datetime.fromtimestamp(pet.searching_till)
                    pet_searching = f"Your pet is searching for __money__. **{pet.name}** will come back {format_dt(pet.searching_till, 'R')}.\n"
                
                else:

                    user: User = await userDH.get(inter.user.id)

                    search_return: int = randint(*Variables.PET_FIND_RETURN)
                    user.balance = user.balance + search_return

                    pet_searching = f"Your pet just came back from searching. **{pet.name}** found {Variables.CURRENCY}``{'{:,}'.format(search_return)}``...\n"
                    pet.searching = False
                    
                    await userDH.update(inter.user.id, "balance", user.balance)
                    await petsDH.update(inter.user.id, "searching", False)


            pet_feed_tip: str = ''
            if pet.hunger > 50:
                pet_feed_tip = f'\n*{pet.name} is hungry, you should feed it...*'

            description = f"{pet_searching}### 🐧 {pet.name}\n\n - :heart: **Health:** {pet.health}** / 100**\n- 🍔 **Hunger:** {pet.hunger}%** / 100%**{pet_feed_tip}\n\n🕓 *Your pet is {'``{:,}``'.format(pet_age_days)} days old.*"

        embed: Embed = Embed(
            title="Virtual pet",
            description=description,
            color=Color.GREEN
        )
        embed.set_footer(text=Default.FOOTER)

        await inter.edit_original_response(embed=embed, view=PetCreation(self.bot) if not pet else PetMainMenu(self.bot, pet))
        

async def setup(bot: Bot):
    await bot.add_cog(PetSimulator(bot))