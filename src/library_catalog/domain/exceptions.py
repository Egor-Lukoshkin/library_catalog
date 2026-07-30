import uuid


class BookNotFoundError(Exception):
    """Книга с указанным идентификатором не найдена."""

    def __init__(self, book_id: uuid.UUID) -> None:
        self.book_id = book_id
        super().__init__(f"Book with id {book_id} was not found")

class BookIsbnAlreadyExistsError(Exception):
    """Книга с указанным ISBN уже существует."""

    def __init__(self, isbn: str) -> None:
        self.isbn = isbn
        super().__init__(f"Book with ISBN {isbn} already exists")