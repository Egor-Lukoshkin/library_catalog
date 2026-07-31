import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status

from ....domain.services.book_service import BookService
from ...dependencies import get_book_service
from ..schemas.book import BookCreate, BookRead


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