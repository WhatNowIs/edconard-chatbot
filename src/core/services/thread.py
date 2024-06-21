from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession as Session
from src.core.models.base import Message, Thread
from src.core.services.service import Service
from src.utils.logger import get_logger

class ThreadService(Service):
    def __init__(self, db_session: Session):
        super().__init__(Thread, db_session)    

    async def get_by_user_id(self, uid: str) -> Optional[Thread]:
        get_logger().info(f"Fetching threads with user id: {uid}")
        async with self.db_session as session:
            result = await session.execute(select(Thread).filter(Thread.user_id == uid))
            return result.scalars().first()
    
    async def get_all_by_user_id(self, uid: str) -> List[Thread]:
        get_logger().info(f"Fetching threads with user id: {uid}")
        async with self.db_session as session:
            result = await session.execute(select(Thread).filter(Thread.user_id == uid))
            return result.scalars().all()        
    
    async def get_by_user_id_and_thread_id(self, uid: str, thread_id) -> List[Thread]:
        get_logger().info(f"Fetching threads with user id: {uid}")
        async with self.db_session as session:
            result = await session.execute(select(Thread).filter(Thread.user_id == uid, Thread.id == thread_id))
            return result.scalars().all()
        
    async def get_messages_by_thread_id(self, uid: str, thread_id: str) -> List[Message]:
        get_logger().info(f"Fetching messages with thread id: {thread_id}")
        
        async with self.db_session as session:
            result = await session.execute(select(Message).filter(Message.thread_id == thread_id, Message.user_id == uid))
            return result.scalars().all()
