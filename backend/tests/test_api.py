from httpx import ASGITransport, AsyncClient

from app.main import app


def client() -> AsyncClient:
    # Lifespan isn't run here, so these tests only cover routes that don't touch the databases.
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


async def test_list_pipelines():
    async with client() as c:
        assert (await c.get("/api/pipelines")).json() == ["bronze_to_silver", "silver_to_gold"]


async def test_unknown_pipeline_404():
    async with client() as c:
        assert (await c.post("/api/pipelines/nope/run")).status_code == 404
