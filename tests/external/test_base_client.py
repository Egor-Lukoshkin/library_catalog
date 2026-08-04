from typing import Any

import httpx
import pytest

from src.library_catalog.external.base.base_client import (
    BaseApiClient,
)


class DummyApiClient(BaseApiClient):
    """Тестовая реализация базового API-клиента."""

    def client_name(self) -> str:
        return "dummy_api_client"

    async def get(self, path: str) -> dict[str, Any]:
        return await self._get(path)


@pytest.mark.asyncio
async def test_request_retries_server_errors_and_succeeds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Повторить запрос после ошибок сервера."""

    attempts = 0
    sleep_calls: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts

        attempts += 1

        if attempts < 3:
            return httpx.Response(
                status_code=500,
                json={"detail": "Server error"},
            )

        return httpx.Response(
            status_code=200,
            json={"status": "ok"},
        )

    async def fake_sleep(delay: float) -> None:
        sleep_calls.append(delay)

    monkeypatch.setattr(
        "src.library_catalog.external.base.base_client"
        ".asyncio.sleep",
        fake_sleep,
    )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(
        transport=transport,
    ) as http_client:
        client = DummyApiClient(
            base_url="https://test.example",
            retries=3,
            backoff=0.5,
            client=http_client,
        )

        result = await client.get("/books")

    assert result == {"status": "ok"}
    assert attempts == 3
    assert sleep_calls == [0.5, 1.0]


@pytest.mark.asyncio
async def test_request_raises_after_all_retries(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Выбросить исключение после исчерпания попыток."""

    attempts = 0
    sleep_calls: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts

        attempts += 1

        return httpx.Response(
            status_code=500,
            json={"detail": "Server error"},
        )

    async def fake_sleep(delay: float) -> None:
        sleep_calls.append(delay)

    monkeypatch.setattr(
        "src.library_catalog.external.base.base_client"
        ".asyncio.sleep",
        fake_sleep,
    )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(
        transport=transport,
    ) as http_client:
        client = DummyApiClient(
            base_url="https://test.example",
            retries=3,
            backoff=0.5,
            client=http_client,
        )

        with pytest.raises(httpx.HTTPStatusError):
            await client.get("/books")

    assert attempts == 3
    assert sleep_calls == [0.5, 1.0]


@pytest.mark.asyncio
async def test_request_does_not_retry_client_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Не повторять запрос после ошибки клиента."""

    attempts = 0
    sleep_calls: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts

        attempts += 1

        return httpx.Response(
            status_code=404,
            json={"detail": "Not found"},
        )

    async def fake_sleep(delay: float) -> None:
        sleep_calls.append(delay)

    monkeypatch.setattr(
        "src.library_catalog.external.base.base_client"
        ".asyncio.sleep",
        fake_sleep,
    )

    transport = httpx.MockTransport(handler)

    async with httpx.AsyncClient(
        transport=transport,
    ) as http_client:
        client = DummyApiClient(
            base_url="https://test.example",
            retries=3,
            backoff=0.5,
            client=http_client,
        )

        with pytest.raises(httpx.HTTPStatusError):
            await client.get("/missing")

    assert attempts == 1
    assert sleep_calls == []