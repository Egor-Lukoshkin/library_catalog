import httpx
import pytest
from httpx import AsyncClient

from tests.conftest import FakeOpenLibraryClient
from tests.test_books import make_book_payload


@pytest.mark.asyncio
async def test_create_book_when_openlibrary_is_unavailable(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Книга создаётся, даже если Open Library недоступна."""

    async def raise_connection_error(
        self: FakeOpenLibraryClient,
        *,
        title: str,
        author: str,
        isbn: str | None = None,
    ) -> None:
        request = httpx.Request(
            "GET",
            "https://openlibrary.org/search.json",
        )

        raise httpx.ConnectError(
            "Open Library is unavailable",
            request=request,
        )

    monkeypatch.setattr(
        FakeOpenLibraryClient,
        "enrich",
        raise_connection_error,
    )

    payload = make_book_payload()

    response = await client.post(
        "/api/v1/books",
        json=payload,
    )

    assert response.status_code == 201

    body = response.json()

    assert body["title"] == payload["title"]
    assert body["author"] == payload["author"]
    assert body["isbn"] == payload["isbn"]
    assert body["extra"] == payload["extra"]