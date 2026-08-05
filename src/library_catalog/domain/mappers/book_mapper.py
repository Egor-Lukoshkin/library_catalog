from collections.abc import Sequence

from ...api.v1.schemas.book import BookRead
from ...data.models.book import Book


class BookMapper:
    """Преобразовывать ORM-модели книг в DTO API."""

    @staticmethod
    def to_read(book: Book) -> BookRead:
        """Преобразовать ORM-модель книги в DTO ответа."""
        return BookRead.model_validate(book)

    @staticmethod
    def to_read_list(books: Sequence[Book]) -> list[BookRead]:
        """Преобразовать последовательность ORM-моделей книг в DTO."""
        return [BookMapper.to_read(book) for book in books]
