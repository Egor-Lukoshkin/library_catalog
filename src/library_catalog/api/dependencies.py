from collections.abc import AsyncGenerator
from typing import Annotated

import httpx
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..data.repositories.book_repository import BookRepository
from ..domain.services.book_service import BookService
from ..external.openlibrary.client import OpenLibraryClient


async def get_book_service(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> AsyncGenerator[BookService, None]:
    """Создать сервис книг для текущего запроса."""
    repository = BookRepository(session)

    http_client = httpx.AsyncClient(
        timeout=10.0,
        trust_env=False,
    )

    openlibrary_client = OpenLibraryClient(
        client=http_client,
    )

    try:
        yield BookService(
            repository=repository,
            openlibrary_client=openlibrary_client,
        )
    finally:
        await openlibrary_client.close()