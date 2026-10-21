from fastapi import APIRouter

from app.db.clickhouse import get_client
from app.db.postgres import get_pool
from app.schemas import DailyRevenue, LayerSummary

router = APIRouter(tags=["layers"])


@router.get("/layers/summary", response_model=LayerSummary)
def layer_summary() -> LayerSummary:
    with get_pool().connection() as conn:
        bronze = conn.execute(
            """
            SELECT count(*)                                    AS total,
                   count(*) FILTER (WHERE processed_at IS NULL) AS pending,
                   count(*) FILTER (WHERE error IS NOT NULL)    AS failed
              FROM bronze.raw_orders
            """
        ).fetchone()
    ch = get_client()
    return LayerSummary(
        bronze_total=bronze["total"],
        bronze_pending=bronze["pending"],
        bronze_failed=bronze["failed"],
        silver_rows=ch.command("SELECT count() FROM silver.orders FINAL"),
        gold_rows=ch.command("SELECT count() FROM gold.daily_revenue FINAL"),
    )


@router.get("/gold/daily-revenue", response_model=list[DailyRevenue])
def daily_revenue(limit: int = 100) -> list[DailyRevenue]:
    result = get_client().query(
        """
        SELECT toString(day) AS day, product, orders, units, toFloat64(revenue) AS revenue
          FROM gold.daily_revenue FINAL
         ORDER BY day DESC, revenue DESC
         LIMIT {limit:UInt32}
        """,
        parameters={"limit": limit},
    )
    return [DailyRevenue(**row) for row in result.named_results()]
