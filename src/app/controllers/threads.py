from typing import List
from src.core.models.base import Thread
from src.utils.logger import get_logger


class ThreadNotFoundError(Exception):
    pass


class ThreadManager():

    @classmethod
    def get_all_threads(cls) -> List[Thread]:
        """
        Fetch and return all thread created by a particular user.
        """

        return []

    @classmethod
    async def create_thread(
        cls, 
    ) -> Thread | None:
        """
        Create a particular thread by user id
        """
        return None

    @classmethod
    def remove_thread(cls) -> None:
        """
        Remove thread for a particular user
        """
        get_logger()
