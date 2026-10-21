from app.core.config import get_settings
from app.db.clickhouse import get_client
from app.db.postgres import get_pool
from app.pipelines.runs import RunStats, track_run
from app.pipelines.transforms import clean_order

SILVER_COLUMNS = [
    "order_id", "customer_id", "product", "quantity", "unit_price",
    "amount", "status", "order_ts", "bronze_id",
]


async def run() -> RunStats:
    """Move unprocessed bronze rows into silver.orders, flagging bad records in bronze."""
    batch_size = get_settings().pipeline_batch_size
    async with track_run("bronze_to_silver") as stats, get_pool().connection() as conn:
        async with conn.transaction():
            cur = await conn.execute(
                """
                SELECT id, payload FROM bronze.raw_orders
                 WHERE processed_at IS NULL
                 ORDER BY id
                 LIMIT %s
                 FOR UPDATE SKIP LOCKED
                """,
                (batch_size,),
            )
            rows = await cur.fetchall()

            good, ok_ids, failures = [], [], []
            for row in rows:
                try:
                    order = clean_order(row["id"], row["payload"])
                except (KeyError, ValueError, TypeError) as exc:
                    failures.append((f"{type(exc).__name__}: {exc}", row["id"]))
                    continue
                good.append([getattr(order, c) for c in SILVER_COLUMNS])
                ok_ids.append(row["id"])

            if good:
                await get_client().insert("silver.orders", good, column_names=SILVER_COLUMNS)

            if ok_ids:
                await conn.execute(
                    "UPDATE bronze.raw_orders SET processed_at = now(), error = NULL"
                    " WHERE id = ANY(%s)",
                    (ok_ids,),
                )
            if failures:
                async with conn.cursor() as cur:
                    await cur.executemany(
                        "UPDATE bronze.raw_orders SET processed_at = now(), error = %s"
                        " WHERE id = %s",
                        failures,
                    )

        stats.processed, stats.failed = len(ok_ids), len(failures)
    return stats
