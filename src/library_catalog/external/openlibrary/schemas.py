from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
)


class OpenLibrarySearchDocument(BaseModel):
    """Отдельная книга из результатов поиска Open Library."""

    model_config = ConfigDict(extra="ignore")

    key: str | None = None
    title: str | None = None
    author_name: list[str] = Field(default_factory=list)
    first_publish_year: int | None = None
    cover_i: int | None = None
    isbn: list[str] = Field(default_factory=list)
    publisher: list[str] = Field(default_factory=list)


class OpenLibrarySearchResponse(BaseModel):
    """Ответ Open Library Search API."""

    model_config = ConfigDict(extra="ignore")

    start: int = 0
    num_found: int = Field(
        default=0,
        validation_alias=AliasChoices(
            "numFound",
            "num_found",
        ),
    )
    docs: list[OpenLibrarySearchDocument] = Field(
        default_factory=list,
    )


class OpenLibraryBookData(BaseModel):
    """Нормализованные сведения для обогащения книги."""

    openlibrary_key: str | None = None
    title: str | None = None
    authors: list[str] = Field(default_factory=list)
    publish_year: int | None = None
    publishers: list[str] = Field(default_factory=list)
    cover_url: str | None = None
    description: str | None = None