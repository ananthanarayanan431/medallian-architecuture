from fastapi import APIRouter
from psycopg.types.json import Jsonb

from app.db.postgres import get_pool
from app.schemas import BronzeIngest

router = APIRouter(prefix="/bronze", tags=["bronze"])


@router.post("/orders", status_code=201)
async def ingest_orders(body: BronzeIngest) -> dict[str, int]:
    """Land raw records as-is. No validation beyond 'is it JSON' — that's silver's job."""
    async with get_pool().connection() as conn, conn.cursor() as cur:
        await cur.executemany(
            "INSERT INTO bronze.raw_orders (source, payload) VALUES (%s, %s)",
            [(body.source, Jsonb(r)) for r in body.records],
        )
    return {"inserted": len(body.records)}
