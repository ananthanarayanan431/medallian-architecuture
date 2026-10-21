from fastapi import APIRouter, HTTPException

from app.db.postgres import get_pool
from app.pipelines.registry import PIPELINES
from app.schemas import PipelineRun

router = APIRouter(prefix="/pipelines", tags=["pipelines"])


@router.get("")
def list_pipelines() -> list[str]:
    return list(PIPELINES)


@router.post("/{name}/run")
def run_pipeline(name: str) -> dict[str, int | str]:
    if name not in PIPELINES:
        raise HTTPException(404, f"unknown pipeline {name!r}")
    stats = PIPELINES[name]()
    return {"pipeline": name, "processed": stats.processed, "failed": stats.failed}


@router.get("/runs", response_model=list[PipelineRun])
def recent_runs(limit: int = 20) -> list[PipelineRun]:
    with get_pool().connection() as conn:
        rows = conn.execute(
            "SELECT * FROM meta.pipeline_runs ORDER BY id DESC LIMIT %s", (limit,)
        ).fetchall()
    return [PipelineRun(**r) for r in rows]
