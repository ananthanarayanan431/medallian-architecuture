from contextlib import contextmanager
from dataclasses import dataclass

from app.db.postgres import get_pool


@dataclass
class RunStats:
    processed: int = 0
    failed: int = 0


@contextmanager
def track_run(pipeline: str):
    """Record a pipeline run in meta.pipeline_runs, marking success or failure."""
    with get_pool().connection() as conn:
        run_id = conn.execute(
            "INSERT INTO meta.pipeline_runs (pipeline, status) VALUES (%s, 'running') RETURNING id",
            (pipeline,),
        ).fetchone()["id"]

    stats = RunStats()
    try:
        yield stats
    except Exception as exc:
        _finish(run_id, "failed", stats, str(exc))
        raise
    _finish(run_id, "succeeded", stats, None)


def _finish(run_id: int, status: str, stats: RunStats, error: str | None) -> None:
    with get_pool().connection() as conn:
        conn.execute(
            """
            UPDATE meta.pipeline_runs
               SET status = %s, rows_processed = %s, rows_failed = %s,
                   finished_at = now(), error = %s
             WHERE id = %s
            """,
            (status, stats.processed, stats.failed, error, run_id),
        )
