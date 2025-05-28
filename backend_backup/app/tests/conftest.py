import pytest
from httpx import AsyncClient
from typing import AsyncGenerator

from app.main import app # Import your FastAPI app

@pytest.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://testserver") as c:
        yield c 