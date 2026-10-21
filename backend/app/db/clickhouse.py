import clickhouse_connect
from clickhouse_connect.driver.asyncclient import AsyncClient

from app.core.config import get_settings

# One shared client: its aiohttp connector is the connection pool.
_client: AsyncClient | None = None


async def open_client() -> None:
    global _client
    if _client is None:
        s = get_settings()
        _client = await clickhouse_connect.get_async_client(
            host=s.clickhouse_host,
            port=s.clickhouse_port,
            username=s.clickhouse_user,
            password=s.clickhouse_password,
            connector_limit=s.clickhouse_pool_size,
            connector_limit_per_host=s.clickhouse_pool_size,
        )


def get_client() -> AsyncClient:
    if _client is None:
        raise RuntimeError("ClickHouse client not open; call open_client() at startup")
    return _client


async def close_client() -> None:
    global _client
    if _client is not None:
        await _client.close()
        _client = None
