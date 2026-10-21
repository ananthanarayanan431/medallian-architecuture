from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_pipelines():
    assert client.get("/api/pipelines").json() == ["bronze_to_silver", "silver_to_gold"]


def test_unknown_pipeline_404():
    assert client.post("/api/pipelines/nope/run").status_code == 404
