import pytest
from httpx import ASGITransport, AsyncClient

from lai.api import app


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_health_keeps_navigation_disabled() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "prototype",
        "version": "0.0.0",
        "navigator_enabled": False,
    }


@pytest.mark.anyio
async def test_query_endpoint_is_unavailable() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        response = await client.post(
            "/navigate", json={"query": "SYNTHETIC administrative request"}
        )
    assert response.status_code == 404
