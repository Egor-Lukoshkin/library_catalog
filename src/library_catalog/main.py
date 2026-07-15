from fastapi import FastAPI

from .core.config import settings

app = FastAPI(
    title=settings.app_name,
    description="REST API для управления книжным каталогом",
    version="1.0.0",
)


@app.get("/")
async def root():
    return {"message": "Welcome to Library Catalog API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}