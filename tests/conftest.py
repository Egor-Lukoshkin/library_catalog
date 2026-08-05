import os
from collections.abc import AsyncGenerator
from typing import Annotated

os.environ["DATABASE_URL"] = (
    "postgresql+asyncpg://postgres:postgres"
    "@localhost:5432/library_catalog_test"
)

import pytest_asyncio
from fastapi import Depends
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.library_catalog.api.dependencies import get_book_service
from src.library_catalog.core.database import (
    Base,
    async_session_maker,
    engine,
    get_db,
)
from src.library_catalog.data.repositories.book_repository import (
    BookRepository,
)
from src.library_catalog.domain.services.book_service import BookService
from src.library_catalog.external.openlibrary.schemas import (
    OpenLibraryBookData,
)
from src.library_catalog.main import app


class FakeOpenLibraryClient:
    """Тестовая замена клиента Open Library без сетевых запросов."""

    async def enrich(
        self,
        *,
        title: str,
        author: str,
        isbn: str | None = None,
    ) -> OpenLibraryBookData:
        return OpenLibraryBookData(
            openlibrary_key="/works/OL_TEST",
            title=title,
            authors=[author],
            publish_year=2000,
            publishers=["Test Publisher"],
            cover_url=(
                "https://covers.openlibrary.org"
                "/b/id/123-L.jpg"
            ),
        )


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def override_get_book_service(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> AsyncGenerator[BookService, None]:
    repository = BookRepository(session)

    yield BookService(
        repository=repository,
        openlibrary_client=FakeOpenLibraryClient(),
    )


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_book_service] = (
        override_get_book_service
    )

    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()

        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)

        await engine.dispose()