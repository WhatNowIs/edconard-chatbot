from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Type, TypeVar, List, Optional
from common.models.base import Base

T = TypeVar('T', bound=Base)

class ChatService:
    def __init__(self, model: Type[T], db_session: AsyncSession):
        self.model = model
        self.db_session = db_session

    async def get_message(self, id: str) -> Optional[T]:
        result = await self.db_session.execute(select(self.model).filter(self.model.id == id))
        return result.scalars().first()

    async def get_all_messages(self) -> List[T]:
        result = await self.db_session.execute(select(self.model))
        return result.scalars().all()

    async def create_message(self, obj_in: T) -> T:
        self.db_session.add(obj_in)
        await self.db_session.commit()
        await self.db_session.refresh(obj_in)
        return obj_in

    async def update_message(self, id: str, obj_in: T) -> Optional[T]:
        db_obj = await self.get_message(id)
        if db_obj:
            for key, value in obj_in.__dict__.items():
                setattr(db_obj, key, value)
            await self.db_session.commit()
            await self.db_session.refresh(db_obj)
            return db_obj

    async def delete_message(self, id: str) -> Optional[T]:
        db_obj = await self.get_message(id)
        if db_obj:
            await self.db_session.delete(db_obj)
            await self.db_session.commit()
            return db_obj
