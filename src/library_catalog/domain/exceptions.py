import uuid

from ..core.exceptions import AppException, NotFoundException


class BookNotFoundError(NotFoundException):
    """Книга с указанным идентификатором не найдена."""

    def __init__(self, book_id: uuid.UUID) -> None:
        self.book_id = book_id
        super().__init__(
            resource="Book",
            identifier=book_id,
        )


class BookIsbnAlreadyExistsError(AppException):
    """Книга с указанным ISBN уже существует."""

    def __init__(self, isbn: str) -> None:
        self.isbn = isbn
        super().__init__(
            message=f"Book with ISBN {isbn} already exists",
            status_code=409,
        )
