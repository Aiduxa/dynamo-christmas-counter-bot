from os import environ, getcwd, listdir
from traceback import print_tb
from typing import Any, List, Mapping, Optional

from discord import Activity, ActivityType, Status, Intents, Embed, Interaction
from discord.ext.commands import Bot, when_mentioned_or
from discord.ext.tasks import loop
from discord.app_commands import AppCommandError

from asyncpg.pool import Pool
from asyncpg import create_pool

from dotenv import load_dotenv

from logging import basicConfig, info, error

load_dotenv(f"{getcwd()}/utils/.env")

from utils import Default, DBGuildNotFound

def format_number(number: int) -> str:
	if number >= 1_000_000:
		return f'{number / 1_000_000:.1f}m'
	elif number >= 1_000:
		return f'{number / 1_000:.1f}k'
	else:
		return str(number)

class Dynamo(Bot):
	def __init__(self, intents: Intents) -> None:
			self.POOL: Pool | None = None
			self.trivia_status: dict = {}

			super().__init__(
				command_prefix=when_mentioned_or(Default.PREFIX),
				case_sensitive=False,
				status=Status.online,
				intents=intents,
				application_id=environ.get("app_id"),
				description="User entertainment bot",
				help_command=None
			)

	
	@loop(minutes=30.0)
	async def continous_handler(self) -> None:
		await self.change_presence(activity=Activity(name=f"{format_number(len(self.users))} users | /help", type=ActivityType.watching))

	@continous_handler.before_loop
	async def before_continous_handler(self) -> None:
		info("waiting to start 'continous_handler'")
		
		await self.wait_until_ready()

		info("started 'continous_handler'")


	async def on_ready(self) -> None:
		info("running")

	async def setup_hook(self) -> None:
		# initalizing database
		db_config = {
		 	'dsn': environ.get("postgres_dsn"),
		 	'user': environ.get("postgres_user"),
		 	'password': environ.get("postgres_password"),
		 	'host': environ.get("postgres_host"),
		 	'database': environ.get("postgres_db"),
		 	'port': environ.get("postgres_port")
		}

		try:
			self.POOL = await create_pool(**db_config)
		except Exception as e:
			error("failed to initialise the database")
			print_tb(e)
		else:
			info("status", "database initialised")

		# loading cogs
		for cog in listdir(f"{getcwd()}/cogs"):
			if not cog.endswith(".py"):
				continue

			try:
				await self.load_extension(f"cogs.{cog[:-3]}")
			except Exception as e:
				error(f"failed to load '{cog}'")
				print_tb(e)
			else:
				info(f"loaded '{cog}'")

		# add jishaku developer commands (https://github.com/Gorialis/jishaku)
		try:
			await self.load_extension('jishaku')
		except Exception as e:
			error("'jishaku' failed to load")
			print_tb(e)
		else:
			info("loaded 'jishaku'")

		# syncing commands
		try:
			await self.tree.sync()
			await self.tree.sync(guild=Default.SERVER)
		except Exception as e:
			error("failed to sync commands")
			print_tb(e)
		else:
			info("synced commands")

		# running background task
		self.continous_handler.start()

intents: Intents = Intents.default()
intents.members = True
intents.messages = True
intents.guilds = True

bot = Dynamo(intents)

if __name__ == '__main__':
	bot.run(environ.get("token"))