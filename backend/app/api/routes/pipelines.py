from fastapi import APIRouter, HTTPException

from app.db.postgres import get_pool
from app.pipelines.registry import PIPELINES
from app.schemas import PipelineRun

router = APIRouter(prefix="/pipelines", tags=["pipelines"])


@router.get("")
async def list_pipelines() -> list[str]:
    return list(PIPELINES)


@router.post("/{name}/run")
async def run_pipeline(name: str) -> dict[str, int | str]:
    if name not in PIPELINES:
        raise HTTPException(404, f"unknown pipeline {name!r}")
    stats = await PIPELINES[name]()
    return {"pipeline": name, "processed": stats.processed, "failed": stats.failed}


@router.get("/runs", response_model=list[PipelineRun])
async def recent_runs(limit: int = 20) -> list[PipelineRun]:
    async with get_pool().connection() as conn:
        cur = await conn.execute(
            "SELECT * FROM meta.pipeline_runs ORDER BY id DESC LIMIT %s", (limit,)
        )
        rows = await cur.fetchall()
    return [PipelineRun(**r) for r in rows]
