from app.db.clickhouse import get_client
from app.pipelines.runs import RunStats, track_run

BUILD_DAILY_REVENUE = """
INSERT INTO gold.daily_revenue (day, product, orders, units, revenue)
SELECT
    toDate(order_ts) AS day,
    product,
    count()          AS orders,
    sum(quantity)    AS units,
    sum(amount)      AS revenue
FROM silver.orders FINAL
WHERE status != 'cancelled'
GROUP BY day, product
"""


async def run() -> RunStats:
    """Rebuild gold aggregates from silver. ReplacingMergeTree keeps the latest per key."""
    async with track_run("silver_to_gold") as stats:
        summary = await get_client().command(BUILD_DAILY_REVENUE)
        stats.processed = int(getattr(summary, "written_rows", 0) or 0)
    return stats
