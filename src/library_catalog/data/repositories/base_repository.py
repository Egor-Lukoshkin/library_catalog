from collections.abc import Sequence
from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import Base


ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Базовый репозиторий для ORM-моделей."""

    def __init__(
        self,
        session: AsyncSession,
        model: type[ModelType],
    ) -> None:
        self.session = session
        self.model = model

    async def create(self, **kwargs: Any) -> ModelType:
        """Создать новую запись."""

        instance = self.model(**kwargs)

        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)

        return instance

    async def get_by_id(self, object_id: Any) -> ModelType | None:
        """Получить запись по первичному ключу."""

        return await self.session.get(self.model, object_id)

    async def get_all(self) -> Sequence[ModelType]:
        """Получить все записи."""

        result = await self.session.scalars(select(self.model))

        return result.all()

    async def update(
            self,
            instance: ModelType,
            **kwargs: Any,
    ) -> ModelType:
        """Обновить существующую запись."""

        for field, value in kwargs.items():
            setattr(instance, field, value)

        await self.session.commit()
        await self.session.refresh(instance)

        return instance

    async def delete(self, instance: ModelType) -> None:
        """Удалить существующую запись."""

        await self.session.delete(instance)
        await self.session.commit()