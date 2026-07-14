from fastapi import FastAPI

app = FastAPI(
    title="Library Catalog API",
    description="REST API для управления книжным каталогом",
    version="1.0.0",
)


@app.get("/")
async def root():
    return {"message": "Welcome to Library Catalog API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}