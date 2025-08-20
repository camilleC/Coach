import pytest
from httpx import AsyncClient
from fastapi import FastAPI

from ragtutor.api.main import app


@pytest.mark.asyncio
async def test_health():
    app.state.skip_init = True
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"

