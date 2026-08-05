from typing import Any

import httpx

from ..base.base_client import BaseApiClient
from .schemas import (
    OpenLibraryBookData,
    OpenLibrarySearchDocument,
    OpenLibrarySearchResponse,
)


class OpenLibraryClient(BaseApiClient):
    """Клиент для работы с Open Library API."""

    def __init__(
        self,
        base_url: str = "https://openlibrary.org",
        timeout: float = 10.0,
        retries: int = 3,
        backoff: float = 0.5,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        super().__init__(
            base_url=base_url,
            timeout=timeout,
            retries=retries,
            backoff=backoff,
            client=client,
        )

    def client_name(self) -> str:
        """Вернуть имя клиента для логирования."""
        return "openlibrary"

    async def search_by_isbn(
        self,
        isbn: str,
    ) -> OpenLibrarySearchDocument | None:
        """Найти книгу по ISBN."""
        return await self._search(
            {
                "isbn": isbn,
                "limit": 1,
            },
        )

    async def search_by_title_author(
        self,
        title: str,
        author: str,
    ) -> OpenLibrarySearchDocument | None:
        """Найти книгу по названию и автору."""
        return await self._search(
            {
                "title": title,
                "author": author,
                "limit": 1,
            },
        )

    async def _search(
        self,
        params: dict[str, Any],
    ) -> OpenLibrarySearchDocument | None:
        """Выполнить поисковый запрос к Open Library."""
        response_data = await self._get(
            "/search.json",
            params=params,
        )

        response = OpenLibrarySearchResponse.model_validate(
            response_data,
        )

        if not response.docs:
            return None

        return response.docs[0]

    async def enrich(
        self,
        *,
        title: str,
        author: str,
        isbn: str | None = None,
    ) -> OpenLibraryBookData | None:
        """Получить дополнительные сведения о книге."""
        document: OpenLibrarySearchDocument | None = None

        if isbn is not None:
            document = await self.search_by_isbn(isbn)

        if document is None:
            document = await self.search_by_title_author(
                title,
                author,
            )

        if document is None:
            return None

        cover_url = None

        if document.cover_i is not None:
            cover_url = (
                "https://covers.openlibrary.org"
                f"/b/id/{document.cover_i}-L.jpg"
            )

        return OpenLibraryBookData(
            openlibrary_key=document.key,
            title=document.title,
            authors=document.author_name,
            publish_year=document.first_publish_year,
            publishers=document.publisher,
            cover_url=cover_url,
        )