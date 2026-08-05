import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any

import httpx


class BaseApiClient(ABC):
    """Базовый клиент для работы с внешними HTTP API."""

    def __init__(
            self,
            base_url: str,
            timeout: float = 10.0,
            retries: int = 3,
            backoff: float = 0.5,
            client: httpx.AsyncClient | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self.backoff = backoff
        self._client = (
            client
            if client is not None
            else httpx.AsyncClient(timeout=self.timeout)
        )
        self.logger = logging.getLogger(
            self.client_name(),
        )

    @abstractmethod
    def client_name(self) -> str:
        """Вернуть имя клиента для логирования."""

    def _build_url(self, path: str) -> str:
        """Построить полный URL запроса."""

        if not path.startswith("/"):
            path = f"/{path}"

        return f"{self.base_url}{path}"

    async def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Выполнить HTTP-запрос с повторными попытками."""

        url = self._build_url(path)

        for attempt in range(self.retries):
            try:
                self.logger.debug(
                    "%s %s params=%s",
                    method,
                    url,
                    params,
                )

                response = await self._client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json,
                    headers=headers,
                )

                response.raise_for_status()

                return response.json()

            except httpx.TimeoutException:
                if attempt == self.retries - 1:
                    self.logger.exception(
                        "Request timed out after %s attempts",
                        self.retries,
                    )
                    raise

                wait_time = self.backoff * (2**attempt)

                self.logger.warning(
                    "Request timed out, retrying in %s seconds",
                    wait_time,
                )

                await asyncio.sleep(wait_time)

            except httpx.HTTPStatusError as error:
                is_server_error = (
                    error.response.status_code >= 500
                )
                has_attempts_left = (
                    attempt < self.retries - 1
                )

                if is_server_error and has_attempts_left:
                    wait_time = self.backoff * (2**attempt)

                    self.logger.warning(
                        "Server error, retrying in %s seconds",
                        wait_time,
                    )

                    await asyncio.sleep(wait_time)
                    continue

                self.logger.exception(
                    "HTTP request failed",
                )
                raise

        raise RuntimeError(
            "HTTP request finished without a response",
        )

    async def _get(
        self,
        path: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Выполнить GET-запрос."""

        return await self._request(
            "GET",
            path,
            **kwargs,
        )

    async def close(self) -> None:
        """Закрыть HTTP-клиент."""

        await self._client.aclose()