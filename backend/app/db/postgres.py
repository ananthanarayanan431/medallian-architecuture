from psycopg import AsyncConnection
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from app.core.config import get_settings

_pool: AsyncConnectionPool[AsyncConnection[dict]] | None = None


async def open_pool() -> None:
    global _pool
    if _pool is None:
        s = get_settings()
        _pool = AsyncConnectionPool(
            s.postgres_dsn,
            min_size=s.postgres_pool_min_size,
            max_size=s.postgres_pool_max_size,
            kwargs={"row_factory": dict_row},
            open=False,
        )
        await _pool.open()


def get_pool() -> AsyncConnectionPool[AsyncConnection[dict]]:
    if _pool is None:
        raise RuntimeError("Postgres pool not open; call open_pool() at startup")
    return _pool


async def close_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
