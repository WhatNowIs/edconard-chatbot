from typing import List, Optional
from sqlalchemy import asc, select
from sqlalchemy.ext.asyncio import AsyncSession as Session
from src.core.models.base import Message, Thread
from src.core.services.service import Service
from src.utils.logger import get_logger

class ThreadService(Service):
    def __init__(self, db_session: Session):
        super().__init__(Thread, db_session)    

    async def get_by_user_id(self, uid: str) -> Optional[Thread]:
        get_logger().info(f"Fetching threads with user id: {uid}")
        # async with self.db_session as session:
        result = await self.db_session.execute(select(Thread).filter(Thread.user_id == uid))
        return result.scalars().first()
    
    async def get_all_by_user_id(self, uid: str) -> List[Thread]:
        get_logger().info(f"Fetching threads with user id: {uid}")
        # async with self.db_session as session:
        result = await self.db_session.execute(select(Thread).filter(Thread.user_id == uid))
        return result.scalars().all()        
    
    async def get_by_user_id_and_thread_id(self, uid: str, thread_id) -> Thread:
        get_logger().info(f"Fetching threads with user id: {uid}")
        # async with self.db_session as session:
        result = await self.db_session.execute(select(Thread).filter(Thread.user_id == uid, Thread.id == thread_id))
        return result.scalars().first()
        
    async def get_messages_by_thread_id(self, uid: str, thread_id: str) -> List[Message]:
        get_logger().info(f"Fetching messages with thread id: {thread_id}")
        
        result = await self.db_session.execute(
            select(Message).filter(Message.thread_id == thread_id, Message.user_id == uid).order_by(asc(Message.timestamp))
        )
        return result.scalars().all()
    
    async def get_threads_by_user_and_workspace(self, user_id: str, workspace_id: str) -> List[Thread]:
        """
        Fetches all threads by user ID and workspace ID.

        Args:
            user_id (str): The ID of the user.
            workspace_id (str): The ID of the workspace.

        Returns:
            List[Thread]: A list of threads associated with the given user and workspace.
        """
        get_logger().info(f"Fetching threads for user id: {user_id} and workspace id: {workspace_id}")
        
        result = await self.db_session.execute(
            select(Thread).filter(Thread.user_id == user_id, Thread.workspace_id == workspace_id)
        )
        return result.scalars().all()
