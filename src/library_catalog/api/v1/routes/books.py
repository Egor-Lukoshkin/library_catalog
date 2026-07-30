import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from ....domain.services.book_service import BookService
from ...dependencies import get_book_service
from ..schemas.book import BookRead


router = APIRouter(
    prefix="/books",
    tags=["books"],
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