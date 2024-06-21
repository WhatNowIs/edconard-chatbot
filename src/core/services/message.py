from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession as Session
from src.core.models.base import Message, Thread
from src.core.services.service import Service
from src.utils.logger import get_logger
from sqlalchemy.orm import joinedload

class MessageService(Service):
    def __init__(self, db_session: Session):
        super().__init__(Message, db_session)    

    async def get_by_user_id(self, uid: str) -> Optional[Message]:
        get_logger().info(f"Fetching credentials with user id: {uid}")
        async with self.db_session as session:
            result = await session.execute(select(Message).filter(Message.user_id == uid))
            return result.scalars().first() 
        
    async def get_thread_by_message_id(self, message_id: str) -> Optional[Thread]:
        get_logger().info(f"Fetching thread with message id: {message_id}")

        async with self.db_session as session:
            result = await session.execute(
                select(Thread)
                .join(Message)
                .filter(Message.id == message_id)
                .options(joinedload(Thread.messages))
            )
            return result.scalars().first()
