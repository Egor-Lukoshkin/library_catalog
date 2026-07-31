from fastapi import FastAPI, Request

from .api.v1.router import api_router
from .core.config import settings

from fastapi.responses import JSONResponse
from .domain.exceptions import (
    BookIsbnAlreadyExistsError,
    BookNotFoundError,
)

app = FastAPI(
    title=settings.app_name,
    description="REST API для управления книжным каталогом",
    version="1.0.0",
)

app.include_router(
    api_router,
    prefix=settings.api_v1_prefix,
)

@app.exception_handler(BookNotFoundError)
async def book_not_found_handler(
    _request: Request,
    error: BookNotFoundError,
) -> JSONResponse:
    """Преобразовать ошибку отсутствующей книги в HTTP 404."""

    return JSONResponse(
        status_code=404,
        content={
            "detail": str(error),
        },
    )

@app.exception_handler(BookIsbnAlreadyExistsError)
async def book_isbn_already_exists_handler(
    _request: Request,
    error: BookIsbnAlreadyExistsError,
) -> JSONResponse:
    """Преобразовать конфликт ISBN в HTTP 409."""

    return JSONResponse(
        status_code=409,
        content={
            "detail": str(error),
        },
    )

@app.get("/")
async def root():
    return {"message": "Welcome to Library Catalog API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}