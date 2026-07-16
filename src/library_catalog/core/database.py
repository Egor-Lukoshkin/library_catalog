from sqlalchemy.ext.asyncio import create_async_engine

from .config import settings


engine = create_async_engine(
    str(settings.database_url),
    echo=settings.debug,
)