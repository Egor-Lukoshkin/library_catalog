import uuid
from typing import Any
from collections.abc import Sequence

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

    async def update_book(
            self,
            book_id: uuid.UUID,
            **changes: Any,
    ) -> Book:
        """Обновить книгу."""

        book = await self.get_book(book_id)

        if "isbn" in changes:
            new_isbn = changes["isbn"]

            if new_isbn is not None and new_isbn != book.isbn:
                existing_book = await self.repository.get_by_isbn(new_isbn)

                if existing_book is not None:
                    raise BookIsbnAlreadyExistsError(new_isbn)

        return await self.repository.update(
            book,
            **changes,
        )

    async def delete_book(self, book_id: uuid.UUID) -> None:
        """Удалить книгу."""

        book = await self.get_book(book_id)

        await self.repository.delete(book)

    async def list_books(
            self,
            *,
            title: str | None = None,
            author: str | None = None,
            genre: str | None = None,
            year: int | None = None,
            available: bool | None = None,
            limit: int = 20,
            offset: int = 0,
    ) -> tuple[Sequence[Book], int]:
        """Получить список книг и их общее количество."""

        books = await self.repository.get_filtered(
            title=title,
            author=author,
            genre=genre,
            year=year,
            available=available,
            limit=limit,
            offset=offset,
        )

        total = await self.repository.count_filtered(
            title=title,
            author=author,
            genre=genre,
            year=year,
            available=available,
        )

        return books, total