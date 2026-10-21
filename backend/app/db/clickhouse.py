import clickhouse_connect
from clickhouse_connect.driver.client import Client

from app.core.config import get_settings


def get_client() -> Client:
    s = get_settings()
    return clickhouse_connect.get_client(
        host=s.clickhouse_host,
        port=s.clickhouse_port,
        username=s.clickhouse_user,
        password=s.clickhouse_password,
    )
