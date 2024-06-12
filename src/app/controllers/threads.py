from typing import Any, List
from src.core.models.base import ConversationThread
from src.utils.logger import get_logger


class ThreadNotFoundError(Exception):
    pass


class ThreadManager():

    @classmethod
    async def get_all_threads(cls) -> List[ConversationThread]:
        """
        Fetch and return all thread created by a particular user.
        """

        return []

    @classmethod
    async def create_thread(
        cls, 
    ) -> ConversationThread | Any:
        """
        Create a particular thread by user id
        """
        return None

    @classmethod
    async def remove_thread(cls):
        """
        Remove thread for a particular user
        """
        get_logger()
