from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from psycopg import AsyncConnection
from psycopg_pool import AsyncConnectionPool

from app.config import settings

pool = None

dsn = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"


@asynccontextmanager
async def get_db_connection() -> AsyncGenerator[AsyncConnection]:
    if not pool:
        raise RuntimeError("Database pool not initialized")
    async with pool.connection() as conn:
        yield conn


async def shutdown():
    """Cleanup function called on shutdown"""
    if pool:
        await pool.close()


async def initialize_pool():
    global pool
    pool = AsyncConnectionPool(conninfo=dsn, min_size=5, max_size=20, timeout=10, open=False)
    await pool.open(wait=True)
