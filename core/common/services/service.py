from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Type, TypeVar, List, Optional
from common.models.base import Base

T = TypeVar('T', bound=Base)

class Service:
    def __init__(self, model: Type[T], db_session: AsyncSession):
        self.model = model
        self.db_session = db_session

    async def get(self, id: str) -> Optional[T]:
        result = await self.db_session.execute(select(self.model).filter(self.model.id == id))
        obj = result.scalars().first()
        if obj is None:
            raise ValueError(f"{self.model.__name__} with id {id} not found")
        return obj

    async def get_all(self) -> List[T]:
        result = await self.db_session.execute(select(self.model))
        return result.scalars().all()

    async def create(self, obj_in: T) -> T:
        self.db_session.add(obj_in)
        await self.db_session.commit()
        await self.db_session.refresh(obj_in)
        return obj_in

    async def update(self, id: str, obj_in: T) -> Optional[T]:
        db_obj = await self.get(id)
        if db_obj:
            for key, value in obj_in.__dict__.items():
                setattr(db_obj, key, value)
            await self.db_session.commit()
            await self.db_session.refresh(db_obj)
            return db_obj
        else:
            raise ValueError(f"{self.model.__name__} with id {id} not found for update")

    async def delete(self, id: str) -> Optional[T]:
        db_obj = await self.get(id)
        if db_obj:
            await self.db_session.delete(db_obj)
            await self.db_session.commit()
            return db_obj
        else:
            raise ValueError(f"{self.model.__name__} with id {id} not found for deletion")