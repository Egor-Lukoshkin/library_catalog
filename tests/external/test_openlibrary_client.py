import httpx
import pytest

from src.library_catalog.external.openlibrary.client import (
    OpenLibraryClient,
)


@pytest.mark.asyncio
async def test_search_by_isbn_returns_book() -> None:
    """Вернуть найденную книгу по ISBN."""

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/search.json"
        assert request.url.params["isbn"] == "9780261103573"
        assert request.url.params["limit"] == "1"

        return httpx.Response(
            status_code=200,
            json={
                "numFound": 1,
                "start": 0,
                "docs": [
                    {
                        "key": "/works/OL27448W",
                        "title": "The Lord of the Rings",
                        "author_name": [
                            "J. R. R. Tolkien",
                        ],
                        "first_publish_year": 1954,
                        "cover_i": 258027,
                        "isbn": [
                            "9780261103573",
                        ],
                        "publisher": [
                            "Allen & Unwin",
                        ],
                    },
                ],
            },
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(
        transport=transport,
    ) as http_client:
        client = OpenLibraryClient(client=http_client)

        book = await client.search_by_isbn(
            "9780261103573",
        )

    assert book is not None
    assert book.key == "/works/OL27448W"
    assert book.title == "The Lord of the Rings"
    assert book.author_name == ["J. R. R. Tolkien"]
    assert book.first_publish_year == 1954
    assert book.cover_i == 258027
    assert book.isbn == ["9780261103573"]
    assert book.publisher == ["Allen & Unwin"]


@pytest.mark.asyncio
async def test_search_by_isbn_returns_none_when_book_not_found() -> None:
    """Вернуть None, если книга не найдена."""

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/search.json"
        assert request.url.params["isbn"] == "0000000000000"
        assert request.url.params["limit"] == "1"

        return httpx.Response(
            status_code=200,
            json={
                "numFound": 0,
                "start": 0,
                "docs": [],
            },
        )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(
        transport=transport,
    ) as http_client:
        client = OpenLibraryClient(client=http_client)

        book = await client.search_by_isbn(
            "0000000000000",
        )

    assert book is None