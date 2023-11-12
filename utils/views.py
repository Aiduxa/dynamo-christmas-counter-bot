__all__ = ["TriviaView"]

from discord.interactions import Interaction
from discord.ui import View, button, Button, Modal, TextInput
from discord.ext.commands import Bot
from discord import Embed

from .objects import User
from .database import userDatabaseHandler
from .default import Color

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
