import uuid
from typing import Any

import pytest
from httpx import AsyncClient


def make_book_payload() -> dict[str, Any]:
    return {
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "year": 2008,
        "genre": "Programming",
        "pages": 464,
        "available": True,
        "isbn": "9780132350884",
        "description": "A handbook of agile software craftsmanship.",
        "extra": {
            "language": "English",
        },
    }


@pytest.mark.asyncio
async def test_create_book(
    client: AsyncClient,
) -> None:
    payload = make_book_payload()

    response = await client.post(
        "/api/v1/books",
        json=payload,
    )

    assert response.status_code == 201

    body = response.json()

    assert uuid.UUID(body["book_id"])
    assert body["title"] == payload["title"]
    assert body["author"] == payload["author"]
    assert body["year"] == payload["year"]
    assert body["genre"] == payload["genre"]
    assert body["pages"] == payload["pages"]
    assert body["available"] is True
    assert body["isbn"] == payload["isbn"]
    assert body["description"] == payload["description"]
    assert body["extra"]["language"] == payload["extra"]["language"]
    assert body["extra"]["openlibrary_key"] is not None
    assert body["extra"]["title"] == payload["title"]
    assert body["extra"]["authors"] == [payload["author"]]
    assert body["created_at"] is not None
    assert body["updated_at"] is not None


@pytest.mark.asyncio
async def test_create_book_with_duplicate_isbn_returns_409(
    client: AsyncClient,
) -> None:
    payload = make_book_payload()

    first_response = await client.post(
        "/api/v1/books",
        json=payload,
    )
    duplicate_response = await client.post(
        "/api/v1/books",
        json=payload,
    )

    assert first_response.status_code == 201
    assert duplicate_response.status_code == 409
    assert duplicate_response.json() == {
        "detail": (
            f"Book with ISBN {payload['isbn']} "
            "already exists"
        ),
    }

@pytest.mark.asyncio
async def test_get_book_by_id(
    client: AsyncClient,
) -> None:
    payload = make_book_payload()

    create_response = await client.post(
        "/api/v1/books",
        json=payload,
    )
    assert create_response.status_code == 201

    created_book = create_response.json()
    book_id = created_book["book_id"]

    response = await client.get(
        f"/api/v1/books/{book_id}",
    )

    assert response.status_code == 200
    assert response.json() == created_book


@pytest.mark.asyncio
async def test_get_nonexistent_book_returns_404(
    client: AsyncClient,
) -> None:
    book_id = uuid.uuid4()

    response = await client.get(
        f"/api/v1/books/{book_id}",
    )

    assert response.status_code == 404

    body = response.json()
    assert "detail" in body
    assert str(book_id) in body["detail"]

@pytest.mark.asyncio
async def test_list_books(
    client: AsyncClient,
) -> None:
    first_payload = make_book_payload()

    second_payload = make_book_payload()
    second_payload["title"] = "Python Crash Course"
    second_payload["author"] = "Eric Matthes"
    second_payload["year"] = 2023
    second_payload["genre"] = "Python"
    second_payload["isbn"] = "9781718502703"

    for payload in (first_payload, second_payload):
        response = await client.post(
            "/api/v1/books",
            json=payload,
        )
        assert response.status_code == 201

    response = await client.get("/api/v1/books")

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 2
    assert body["limit"] == 20
    assert body["offset"] == 0
    assert len(body["items"]) == 2

    returned_isbns = {
        book["isbn"]
        for book in body["items"]
    }
    assert returned_isbns == {
        first_payload["isbn"],
        second_payload["isbn"],
    }


@pytest.mark.asyncio
async def test_list_books_filtered_by_author(
    client: AsyncClient,
) -> None:
    first_payload = make_book_payload()

    second_payload = make_book_payload()
    second_payload["title"] = "Python Crash Course"
    second_payload["author"] = "Eric Matthes"
    second_payload["year"] = 2023
    second_payload["genre"] = "Python"
    second_payload["isbn"] = "9781718502703"

    for payload in (first_payload, second_payload):
        response = await client.post(
            "/api/v1/books",
            json=payload,
        )
        assert response.status_code == 201

    response = await client.get(
        "/api/v1/books",
        params={
            "author": "Eric Matthes",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 1
    assert body["limit"] == 20
    assert body["offset"] == 0
    assert len(body["items"]) == 1
    assert body["items"][0]["title"] == second_payload["title"]
    assert body["items"][0]["author"] == second_payload["author"]
    assert body["items"][0]["isbn"] == second_payload["isbn"]

@pytest.mark.asyncio
async def test_update_book(
    client: AsyncClient,
) -> None:
    create_response = await client.post(
        "/api/v1/books",
        json=make_book_payload(),
    )
    assert create_response.status_code == 201

    created_book = create_response.json()
    book_id = created_book["book_id"]

    response = await client.patch(
        f"/api/v1/books/{book_id}",
        json={
            "title": "Clean Architecture",
            "pages": 432,
            "available": False,
        },
    )

    assert response.status_code == 200

    updated_book = response.json()

    assert updated_book["book_id"] == book_id
    assert updated_book["title"] == "Clean Architecture"
    assert updated_book["pages"] == 432
    assert updated_book["available"] is False

    assert updated_book["author"] == created_book["author"]
    assert updated_book["isbn"] == created_book["isbn"]
    assert updated_book["description"] == created_book["description"]
    assert updated_book["extra"] == created_book["extra"]


@pytest.mark.asyncio
async def test_delete_book(
    client: AsyncClient,
) -> None:
    create_response = await client.post(
        "/api/v1/books",
        json=make_book_payload(),
    )
    assert create_response.status_code == 201

    book_id = create_response.json()["book_id"]

    delete_response = await client.delete(
        f"/api/v1/books/{book_id}",
    )

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    get_response = await client.get(
        f"/api/v1/books/{book_id}",
    )

    assert get_response.status_code == 404
    assert str(book_id) in get_response.json()["detail"]

@pytest.mark.asyncio
async def test_update_book_with_null_required_field_returns_422(
    client: AsyncClient,
) -> None:
    create_response = await client.post(
        "/api/v1/books",
        json=make_book_payload(),
    )
    assert create_response.status_code == 201

    book_id = create_response.json()["book_id"]

    response = await client.patch(
        f"/api/v1/books/{book_id}",
        json={
            "title": None,
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_book_with_duplicate_isbn_returns_409(
    client: AsyncClient,
) -> None:
    first_payload = make_book_payload()

    second_payload = make_book_payload()
    second_payload["title"] = "Python Crash Course"
    second_payload["isbn"] = "9781718502703"

    first_response = await client.post(
        "/api/v1/books",
        json=first_payload,
    )
    second_response = await client.post(
        "/api/v1/books",
        json=second_payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    second_book_id = second_response.json()["book_id"]

    response = await client.patch(
        f"/api/v1/books/{second_book_id}",
        json={
            "isbn": first_payload["isbn"],
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": (
            f"Book with ISBN {first_payload['isbn']} "
            "already exists"
        ),
    }


@pytest.mark.asyncio
async def test_update_nonexistent_book_returns_404(
    client: AsyncClient,
) -> None:
    book_id = uuid.uuid4()

    response = await client.patch(
        f"/api/v1/books/{book_id}",
        json={
            "title": "New title",
        },
    )

    assert response.status_code == 404
    assert str(book_id) in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_nonexistent_book_returns_404(
    client: AsyncClient,
) -> None:
    book_id = uuid.uuid4()

    response = await client.delete(
        f"/api/v1/books/{book_id}",
    )

    assert response.status_code == 404
    assert str(book_id) in response.json()["detail"]

@pytest.mark.asyncio
async def test_list_books_filtered_by_title(
    client: AsyncClient,
) -> None:
    first_payload = make_book_payload()

    second_payload = make_book_payload()
    second_payload["title"] = "Python Crash Course"
    second_payload["author"] = "Eric Matthes"
    second_payload["isbn"] = "9781718502703"

    for payload in (first_payload, second_payload):
        response = await client.post(
            "/api/v1/books",
            json=payload,
        )
        assert response.status_code == 201

    response = await client.get(
        "/api/v1/books",
        params={
            "title": "clean",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["title"] == first_payload["title"]
    assert body["items"][0]["isbn"] == first_payload["isbn"]

@pytest.mark.asyncio
async def test_list_books_filtered_by_exact_genre(
    client: AsyncClient,
) -> None:
    first_payload = make_book_payload()
    first_payload["genre"] = "Programming"

    second_payload = make_book_payload()
    second_payload["title"] = "Python Crash Course"
    second_payload["author"] = "Eric Matthes"
    second_payload["genre"] = "Program"
    second_payload["isbn"] = "9781718502703"

    for payload in (first_payload, second_payload):
        response = await client.post(
            "/api/v1/books",
            json=payload,
        )
        assert response.status_code == 201

    response = await client.get(
        "/api/v1/books",
        params={
            "genre": "Program",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["title"] == second_payload["title"]
    assert body["items"][0]["genre"] == "Program"
    assert body["items"][0]["isbn"] == second_payload["isbn"]