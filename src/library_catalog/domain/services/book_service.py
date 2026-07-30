import uuid
from typing import Any

from ...data.models.book import Book
from ...data.repositories.book_repository import BookRepository
from ..exceptions import (
    BookIsbnAlreadyExistsError,
    BookNotFoundError,
)


class BookService:
    """Сервис бизнес-логики для книг."""

    def __init__(self, repository: BookRepository) -> None:
        self.repository = repository

    async def get_book(self, book_id: uuid.UUID) -> Book:
        """Получить книгу или сообщить, что она не найдена."""

        book = await self.repository.get_by_id(book_id)

        if book is None:
            raise BookNotFoundError(book_id)

        return book

    async def create_book(
            self,
            *,
            title: str,
            author: str,
            year: int,
            genre: str,
            pages: int,
            available: bool = True,
            isbn: str | None = None,
            description: str | None = None,
            extra: dict[str, Any] | None = None,
    ) -> Book:
        """Создать книгу."""

        if isbn is not None:
            existing_book = await self.repository.get_by_isbn(isbn)

            if existing_book is not None:
                raise BookIsbnAlreadyExistsError(isbn)

        return await self.repository.create(
            title=title,
            author=author,
            year=year,
            genre=genre,
            pages=pages,
            available=available,
            isbn=isbn,
            description=description,
            extra=extra,
        )