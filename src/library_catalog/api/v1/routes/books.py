import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from ....domain.services.book_service import BookService
from ...dependencies import get_book_service
from ..schemas.book import (
    BookCreate,
    BookList,
    BookRead,
    BookUpdate,
)


router = APIRouter(
    prefix="/books",
    tags=["books"],
)


@router.post(
    "",
    response_model=BookRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_book(
    book_data: BookCreate,
    service: Annotated[
        BookService,
        Depends(get_book_service),
    ],
) -> BookRead:
    """Создать книгу."""

    book = await service.create_book(
        **book_data.model_dump(),
    )

    return BookRead.model_validate(book)

@router.get(
    "",
    response_model=BookList,
)
async def list_books(
    service: Annotated[
        BookService,
        Depends(get_book_service),
    ],
    author: Annotated[
        str | None,
        Query(
            min_length=1,
            max_length=300,
        ),
    ] = None,
    genre: Annotated[
        str | None,
        Query(
            min_length=1,
            max_length=100,
        ),
    ] = None,
    year: Annotated[
        int | None,
        Query(
            ge=1000,
            le=2100,
        ),
    ] = None,
    available: bool | None = None,
    limit: Annotated[
        int,
        Query(
            ge=1,
            le=100,
        ),
    ] = 20,
    offset: Annotated[
        int,
        Query(ge=0),
    ] = 0,
) -> BookList:
    """Получить список книг."""

    books, total = await service.list_books(
        author=author,
        genre=genre,
        year=year,
        available=available,
        limit=limit,
        offset=offset,
    )

    return BookList(
        items=[
            BookRead.model_validate(book)
            for book in books
        ],
        total=total,
        limit=limit,
        offset=offset,
    )

@router.get(
    "/{book_id}",
    response_model=BookRead,
)
async def get_book(
    book_id: uuid.UUID,
    service: Annotated[
        BookService,
        Depends(get_book_service),
    ],
) -> BookRead:
    """Получить книгу по идентификатору."""

    book = await service.get_book(book_id)

    return BookRead.model_validate(book)

@router.patch(
    "/{book_id}",
    response_model=BookRead,
)
async def update_book(
    book_id: uuid.UUID,
    book_data: BookUpdate,
    service: Annotated[
        BookService,
        Depends(get_book_service),
    ],
) -> BookRead:
    """Частично обновить книгу."""

    changes = book_data.model_dump(
        exclude_unset=True,
    )

    book = await service.update_book(
        book_id,
        **changes,
    )

    return BookRead.model_validate(book)

@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_book(
    book_id: uuid.UUID,
    service: Annotated[
        BookService,
        Depends(get_book_service),
    ],
) -> None:
    """Удалить книгу по идентификатору."""

    await service.delete_book(book_id)