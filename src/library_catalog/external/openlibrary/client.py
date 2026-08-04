from typing import Any

import httpx
from ..base.base_client import BaseApiClient
from .schemas import (
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

        params: dict[str, Any] = {
            "isbn": isbn,
            "limit": 1,
        }

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