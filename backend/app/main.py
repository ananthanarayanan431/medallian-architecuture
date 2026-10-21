from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import bronze, health, layers, pipelines
from app.db import clickhouse, postgres


@asynccontextmanager
async def lifespan(_: FastAPI):
    await postgres.open_pool()
    await clickhouse.open_client()
    try:
        yield
    finally:
        await clickhouse.close_client()
        await postgres.close_pool()


app = FastAPI(title="Medallion Architecture API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in (health.router, bronze.router, layers.router, pipelines.router):
    app.include_router(r, prefix="/api")
