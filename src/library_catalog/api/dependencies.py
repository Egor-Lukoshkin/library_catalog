from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..data.repositories.book_repository import BookRepository
from ..domain.services.book_service import BookService


def get_book_service(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> BookService:
    """Создать сервис книг для текущего запроса."""

    repository = BookRepository(session)

    return BookService(repository)