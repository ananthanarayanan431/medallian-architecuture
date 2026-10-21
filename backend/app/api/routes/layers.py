import asyncio

from fastapi import APIRouter

from app.db.clickhouse import get_client
from app.db.postgres import get_pool
from app.schemas import DailyRevenue, LayerSummary

router = APIRouter(tags=["layers"])


async def _bronze_counts() -> dict[str, int]:
    async with get_pool().connection() as conn:
        cur = await conn.execute(
            """
            SELECT count(*)                                    AS total,
                   count(*) FILTER (WHERE processed_at IS NULL) AS pending,
                   count(*) FILTER (WHERE error IS NOT NULL)    AS failed
              FROM bronze.raw_orders
            """
        )
        return await cur.fetchone()


@router.get("/layers/summary", response_model=LayerSummary)
async def layer_summary() -> LayerSummary:
    ch = get_client()
    bronze, silver_rows, gold_rows = await asyncio.gather(
        _bronze_counts(),
        ch.command("SELECT count() FROM silver.orders FINAL"),
        ch.command("SELECT count() FROM gold.daily_revenue FINAL"),
    )
    return LayerSummary(
        bronze_total=bronze["total"],
        bronze_pending=bronze["pending"],
        bronze_failed=bronze["failed"],
        silver_rows=silver_rows,
        gold_rows=gold_rows,
    )


@router.get("/gold/daily-revenue", response_model=list[DailyRevenue])
async def daily_revenue(limit: int = 100) -> list[DailyRevenue]:
    result = await get_client().query(
        """
        SELECT toString(day) AS day, product, orders, units, toFloat64(revenue) AS revenue
          FROM gold.daily_revenue FINAL
         ORDER BY day DESC, revenue DESC
         LIMIT {limit:UInt32}
        """,
        parameters={"limit": limit},
    )
    return [DailyRevenue(**row) for row in result.named_results()]
