import os
from collections.abc import AsyncGenerator

os.environ["DATABASE_URL"] = (
    "postgresql+asyncpg://postgres:postgres"
    "@localhost:5432/library_catalog_test"
)

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.library_catalog.core.database import (
    Base,
    async_session_maker,
    engine,
    get_db,
)
from src.library_catalog.main import app


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as test_client:
        yield test_client

    app.dependency_overrides.clear()

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)

    await engine.dispose()