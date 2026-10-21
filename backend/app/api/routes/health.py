from fastapi import APIRouter

from app.db.clickhouse import get_client
from app.db.postgres import get_pool

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    result = {"status": "ok", "postgres": "ok", "clickhouse": "ok"}
    try:
        with get_pool().connection(timeout=2) as conn:
            conn.execute("SELECT 1")
    except Exception as exc:  # noqa: BLE001 - report any failure as degraded
        result.update(status="degraded", postgres=str(exc))
    try:
        if not get_client().ping():
            raise RuntimeError("ping failed")
    except Exception as exc:  # noqa: BLE001
        result.update(status="degraded", clickhouse=str(exc))
    return result
