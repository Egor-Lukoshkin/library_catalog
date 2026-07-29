import uuid
from datetime import datetime
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationInfo,
    field_validator,
)


class BookBase(BaseModel):
    """Базовая схема с общими полями книги."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    title: str = Field(
        ...,
        min_length=1,
        max_length=500,
    )

    author: str = Field(
        ...,
        min_length=1,
        max_length=300,
    )

    year: int = Field(
        ...,
        ge=1000,
        le=2100,
    )

    genre: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    pages: int = Field(
        ...,
        gt=0,
    )

class BookCreate(BookBase):
    """Схема создания книги."""

    available: bool = True

    isbn: str | None = Field(
        default=None,
        min_length=1,
        max_length=20,
    )

    description: str | None = None

    extra: dict[str, Any] | None = None

class BookUpdate(BaseModel):
    """Схема обновления книги."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
    )

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=500,
    )

    author: str | None = Field(
        default=None,
        min_length=1,
        max_length=300,
    )

    year: int | None = Field(
        default=None,
        ge=1000,
        le=2100,
    )

    genre: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    pages: int | None = Field(
        default=None,
        gt=0,
    )

    available: bool | None = None

    isbn: str | None = Field(
        default=None,
        min_length=1,
        max_length=20,
    )

    description: str | None = None

    extra: dict[str, Any] | None = None

    @field_validator(
        "title",
        "author",
        "year",
        "genre",
        "pages",
        "available",
    )
    @classmethod
    def reject_null_for_required_fields(
        cls,
        value: Any,
        info: ValidationInfo,
    ) -> Any:
        """Запретить null для обязательных полей модели."""

        if value is None:
            raise ValueError(
                f"{info.field_name} cannot be null",
            )

        return value

class BookRead(BookBase):
    """Схема книги в ответе API."""

    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
    )

    book_id: uuid.UUID
    available: bool
    isbn: str | None
    description: str | None
    extra: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime

class BookList(BaseModel):
    """Схема списка книг с пагинацией."""

    items: list[BookRead]

    total: int = Field(
        ...,
        ge=0,
    )

    limit: int = Field(
        ...,
        gt=0,
    )

    offset: int = Field(
        ...,
        ge=0,
    )