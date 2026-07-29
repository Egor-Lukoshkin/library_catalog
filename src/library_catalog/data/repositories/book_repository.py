from collections.abc import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.book import Book
from .base_repository import BaseRepository


class BookRepository(BaseRepository[Book]):
    """Репозиторий для работы с книгами."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Book)

    async def get_by_isbn(self, isbn: str) -> Book | None:
        """Получить книгу по ISBN."""

        statement = select(Book).where(Book.isbn == isbn)

        return await self.session.scalar(statement)

    async def get_filtered(
            self,
            *,
            author: str | None = None,
            genre: str | None = None,
            year: int | None = None,
            available: bool | None = None,
            limit: int = 20,
            offset: int = 0,
    ) -> Sequence[Book]:
        """Получить книги с фильтрацией и пагинацией."""

        statement = select(Book)

        if author is not None:
            statement = statement.where(
                Book.author.ilike(f"%{author}%"),
            )

        if genre is not None:
            statement = statement.where(
                Book.genre.ilike(f"%{genre}%"),
            )

        if year is not None:
            statement = statement.where(Book.year == year)

        if available is not None:
            statement = statement.where(Book.available == available)

        statement = (
            statement
            .order_by(Book.book_id)
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.scalars(statement)

        return result.all()