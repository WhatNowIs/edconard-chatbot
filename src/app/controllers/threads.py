from typing import Any, List
from src.core.models.base import Thread
from src.utils.logger import get_logger
from src.core.services.chat import ChatService
from sqlalchemy.ext.asyncio import AsyncSession

class ThreadManager:
    @classmethod
    async def get_all_threads(cls, db_session: AsyncSession) -> List[Thread]:
        chat_service = ChatService(Thread, db_session)
        return await chat_service.get_all_messages()

    @classmethod
    async def create_thread(cls, db_session: AsyncSession, thread: Thread) -> Thread:
        chat_service = ChatService(Thread, db_session)
        return await chat_service.create_message(thread)

    @classmethod
    async def remove_thread(cls, db_session: AsyncSession, thread_id: str):
        chat_service = ChatService(Thread, db_session)
        await chat_service.delete_message(thread_id)
        get_logger().info(f"Thread {thread_id} removed successfully.")
