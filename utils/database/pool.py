import asyncio
import ssl

from asyncpg import pool, create_pool
from os import environ, getcwd
from dotenv import load_dotenv

load_dotenv(f"{getcwd()}/utils/.env")


async def init() ->  pool.Pool:

    sql_config = {
    'dsn': environ.get("postgres_dsn"),
    'user': environ.get("postgres_user"),
    'password': environ.get("postgres_password"),
    'host': environ.get("host"),
    'database': environ.get("database"),
    'port': environ.get("port")
    }
    
    ctx = ssl.create_default_context(cafile='')
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    global POOL
    POOL = await create_pool(**sql_config, ssl=ctx)