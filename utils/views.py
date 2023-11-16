__all__ = ["TriviaView", "PetMainMenu", "PetCreation"]

from discord.interactions import Interaction
from discord.ui import View, button, Button, Modal, TextInput
from discord.ext.commands import Bot
from discord import Embed
from discord.utils import format_dt

from time import time
from datetime import datetime

from .objects import User, Pet
from .database import userDatabaseHandler, petsDatabaseHandler
from .default import Color, Variables, Default

class TriviaModal(Modal, title="🎅 Dynamo's christmas themed trivia"):

    def __init__(self, bot: Bot, question: dict, points: int, trivia_id: float) -> None:
        self.bot: Bot = bot
        self.question: dict = question
        self.points: int = points
        self.trivia_id: float = trivia_id
        super().__init__(custom_id="christmastriviamodal")
        self.add_item(
            TextInput(label="Answer", placeholder="Write your answer here", max_length=50, custom_id="answer")
        )

    async def on_submit(self, inter: Interaction) -> None:

        if not str(self.children[0]).lower() == str(self.question["answer"]):
            await inter.response.send_message("Wrong answer, try again.", ephemeral=True)
            return

        await inter.response.edit_message(content="")

        userDH: userDatabaseHandler = userDatabaseHandler(self.bot.POOL)

        user: User = await userDH.get(inter.user.id)

        user.trivia_points += self.points

        await userDH.update(inter.user.id, "trivia_points", user.trivia_points)

        embed = Embed(
        title="🎅 Christmas trivia",
        description=f"\n## Q: {self.question['question']}\nAnswer: {' '.join(list(str(self.question['answer']).upper()))}\n✔ **Answered by:** {inter.user.mention}",
        color=Color.GREEN
        )
        await inter.edit_original_response(embed=embed, view=None)
        self.bot.trivia_status[self.trivia_id] = True

class TriviaView(View):

    def __init__(self, bot: Bot, question: dict, points: int, trivia_id: float):
        self.bot: Bot = bot
        self.question: dict = question
        self.points: int = points
        self.trivia_id: float = trivia_id
        super().__init__(timeout=30.0)

    async def on_timeout(self) -> None:
        self.answer_button.disabled = True

        self.clear_items()

    @button(label="Write answer")
    async def answer_button(self, inter: Interaction, button: Button) -> None:

        await inter.response.send_modal(TriviaModal(self.bot, self.question, self.points, self.trivia_id))

def gen_pet_embed(pet: Pet) -> Embed:
    
        pet_age_days: int = int(float(time() - pet.created_at.timestamp()) / 86400)

        pet_searching: str = ''
        if pet.searching:
            pet.searching_till = datetime.fromtimestamp(pet.searching_till)
            pet_searching = f"Your pet is searching for __money__. **{pet.name}** will come back {format_dt(pet.searching_till, 'R')}.\n"

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

        return embed

class PetCreationModal(Modal):

    def __init__(self, bot: Bot):
        self.bot: Bot = bot
        super().__init__(title="Virtual pets")
        self.add_item(
            TextInput(label="Pet's name", placeholder="Enter your pet's name", required=True, max_length=100)
        )

    async def on_submit(self, inter: Interaction) -> None:
        
        await inter.response.edit_message(content="")
        
        petsDH: petsDatabaseHandler = petsDatabaseHandler(self.bot.POOL)

        await petsDH.create(inter.user.id)

        pet: Pet = await petsDH.get(inter.user.id)

        pet.name = str(self.children[0])

        await petsDH.update(inter.user.id, "name", pet.name)

        embed: Embed = gen_pet_embed(pet)    

        await inter.edit_original_response(embed=embed, view=PetMainMenu(self.bot, pet))

class PetCreation(View):

    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot
        super().__init__()

    @button(label="Look for a pet", emoji="🐧")
    async def look_for_pet_button(self, inter: Interaction, button: Button):

        petsDH: petsDatabaseHandler = petsDatabaseHandler(self.bot.POOL)

        pet: Pet | None = await petsDH.get(inter.user.id)

        if not pet:
            await inter.response.send_modal(PetCreationModal(self.bot))
        else:
            await inter.response.send_message("Something went wrong, please contact support", ephemeral=True)



class PetMainMenu(View):

    def __init__(self, bot: Bot, pet: Pet):
        self.bot: Bot = bot
        self.pet: Pet = pet
        super().__init__()

        if not self.pet.searching:
            self.search_button.disabled = False
            self.feed_button.disabled = False

        if self.pet.hunger == 0:
            self.feed_button.disabled = True

    @button(label="Send Pet to search", disabled=True, emoji="🔎")
    async def search_button(self, inter: Interaction, button: Button) -> None:

        await inter.response.edit_message(content="")

        petDH: petsDatabaseHandler = petsDatabaseHandler(self.bot.POOL)

        await petDH.update(self.pet.owner_id, "searching", True)
        await petDH.update(self.pet.owner_id, "searching_till", time() + Variables.PET_FIND_COOLDOWN)

        self.pet = await petDH.get(self.pet.owner_id)
        
        embed: Embed = gen_pet_embed(self.pet)

        await inter.edit_original_response(embed=embed, view=PetMainMenu(self.bot, self.pet))
    
    @button(label="Feed pet", disabled=True, emoji="🍔")
    async def feed_button(self, inter: Interaction, button: Button) -> None:

        await inter.response.edit_message(content="")

        petDH: petsDatabaseHandler = petsDatabaseHandler(self.bot.POOL)
        userDH: userDatabaseHandler = userDatabaseHandler(self.bot.POOL)

        user: User = await userDH.get(inter.user.id)

        user.balance = user.balance - int(Variables.PET_FEED_COST / float(self.pet.hunger / 100))
        self.pet.hunger = 0

        await userDH.update(inter.user.id, "balance", user.balance)

        await petDH.update(self.pet.owner_id, "hunger", self.pet.hunger)

        self.pet = await petDH.get(self.pet.owner_id)
        
        embed: Embed = gen_pet_embed(self.pet)

        await inter.edit_original_response(embed=embed, view=PetMainMenu(self.bot, self.pet))