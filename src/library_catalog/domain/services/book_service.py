import uuid

from ...data.models.book import Book
from ...data.repositories.book_repository import BookRepository
from ..exceptions import BookNotFoundError


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