__all__ = ["userDatabaseHandler", "serverDatabaseHandler"]

from asyncpg.pool import Pool
from asyncpg import Record
from time import time
from json import loads, dumps
from datetime import datetime
from dacite import from_dict

from .errors import DBGuildNotFound, DBUserNotFound
from .default import Default
from .objects import User, Server

class Database:

	def __init__(self, pool: Pool) -> None:
		self.pool: Pool = pool

	async def get_db_latency(self) -> float:
		old: float = time()

		async with self.pool.acquire() as conn:
			await conn.execute("SELECT now()")

		return time() - old
	
	async def fetch(self, query, *args) -> list[Record]:
		async with self.pool.acquire() as conn:
			data: list[Record] = await conn.fetch(query, *args)
		return data
	
	async def fetchval(self, query, *args) -> Record:
		async with self.pool.acquire() as conn:
			data: Record = await conn.fetchval(query, *args)
		return data
	
	async def fetchrow(self, query, *args) -> Record:
		async with self.pool.acquire() as conn:
			data: Record = await conn.fetchrow(query, *args)
		return data
	
	async def execute(self, query, *args) -> None:
		async with self.pool.acquire() as conn:
			await conn.execute(query, *args)

class userDatabaseHandler(Database): 

	def __init__(self, pool: Pool) -> None:
		self.pool: Pool = pool
		super().__init__(pool=pool)

	async def create(self, user_id: int) -> None:
		await self.execute("INSERT INTO users (id) VALUES ($1)", user_id)

	async def get(self, user_id: int) -> User:
		data: Record = await self.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
		if not data:
			await self.create(user_id=user_id)
			data: Record = await self.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
		return from_dict(User, dict(data))

	async def delete(self, user_id: int) -> None:
		await self.execute("DELETE FROM users WHERE id = 1")
	
	async def update(self, user_id: int, column: str, new_value: str | int | float | bool | None) -> User:
		data: Record = await self.execute(f"UPDATE users SET {column} = $2 WHERE id = $1", user_id, new_value)

	async def get_trivia_leaderboard(self) -> User:
		data: list[Record] = await self.fetch("SELECT id, trivia_points, RANK() OVER (ORDER BY trivia_points DESC) as trivia_ranking, created_at FROM users ORDER BY trivia_points DESC")
		return [from_dict(User, user) for user in data]

	async def get_trivia_ranking(self, user_id: int) -> User:
		data: Record = await self.fetchrow("SELECT id, trivia_points, RANK() OVER (ORDER BY trivia_points DESC) as trivia_ranking, created_at FROM users WHERE id = $1", user_id)
		return from_dict(User, data)

class serverDatabaseHandler(Database): 

	def __init__(self, pool: Pool) -> None:
		self.pool: Pool = pool
		super().__init__(pool=pool)

	async def create(self, server_id: int) -> None:
		await self.execute("INSERT INTO servers (id) VALUES ($1)", server_id)

	async def get(self, server_id: int) -> Server:
		data: Record = await self.fetchrow("SELECT * FROM servers WHERE id = $1", server_id)
		if not data:
			await self.create(server_id=server_id)
			data: Record = await self.fetchrow("SELECT * FROM servers WHERE id = $1", server_id)
		return from_dict(Server, dict(data))
	
	async def getAll(self) -> list[Server]:
		data: list[Record] = await self.fetch("SELECT * FROM servers WHERE christmas_countdown_channel_id IS NOT NULL AND christmas_countdown_message_id IS NOT NULL")
		return [from_dict(Server, dict(server)) for server in data]

	async def delete(self, server_id: int) -> None:
		await self.execute("DELETE FROM servers WHERE id = 1")
	
	async def update(self, server_id: int, column: str, new_value: str | int | float | bool | None) -> Server:
		await self.execute(f"UPDATE servers SET {column} = $2 WHERE id = $1", server_id, new_value)
		
	