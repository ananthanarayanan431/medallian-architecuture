from contextlib import asynccontextmanager
from dataclasses import dataclass

from app.db.postgres import get_pool


@dataclass
class RunStats:
    processed: int = 0
    failed: int = 0


@asynccontextmanager
async def track_run(pipeline: str):
    """Record a pipeline run in meta.pipeline_runs, marking success or failure."""
    async with get_pool().connection() as conn:
        cur = await conn.execute(
            "INSERT INTO meta.pipeline_runs (pipeline, status) VALUES (%s, 'running') RETURNING id",
            (pipeline,),
        )
        run_id = (await cur.fetchone())["id"]

    stats = RunStats()
    try:
        yield stats
    except Exception as exc:
        await _finish(run_id, "failed", stats, str(exc))
        raise
    await _finish(run_id, "succeeded", stats, None)


async def _finish(run_id: int, status: str, stats: RunStats, error: str | None) -> None:
    async with get_pool().connection() as conn:
        await conn.execute(
            """
            UPDATE meta.pipeline_runs
               SET status = %s, rows_processed = %s, rows_failed = %s,
                   finished_at = now(), error = %s
             WHERE id = %s
            """,
            (status, stats.processed, stats.failed, error, run_id),
        )
