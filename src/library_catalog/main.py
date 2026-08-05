from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api.v1.router import api_router
from .core.config import settings
from .core.database import dispose_engine
from .core.exceptions import register_exception_handlers
from .core.logging_config import setup_logging


@asynccontextmanager
async def lifespan(
    _app: FastAPI,
) -> AsyncIterator[None]:
    """Управлять запуском и завершением приложения."""
    setup_logging()

    yield

    await dispose_engine()


app = FastAPI(
    title=settings.app_name,
    description="REST API для управления книжным каталогом",
    version="1.0.0",
    lifespan=lifespan,
)

register_exception_handlers(app)

app.include_router(
    api_router,
    prefix=settings.api_v1_prefix,
)


@app.get("/")
async def root() -> dict[str, str]:
    """Вернуть информацию о приложении."""
    return {
        "message": "Welcome to Library Catalog API",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Проверить работоспособность приложения."""
    return {"status": "healthy"}
