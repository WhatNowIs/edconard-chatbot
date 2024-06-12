from typing import List
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from src.core.models.base import Thread
from src.app.controllers.threads import ThreadManager


threads_router = r = APIRouter()


@r.get("")
async def fetch_threads() -> List[Thread]:
    """
    Get the current threads.
    """
    return await ThreadManager.get_all_threads()


@r.post("")
async def create_thread() -> Thread | None:
    """
    Create a new thread.
    """
    res = await ThreadManager.create_thread()
    return res


@r.delete("/{thread_id}")
async def remove_thread(thread_id: str) -> None:
    """
    Remove a thread.
    """
    ThreadManager.remove_thread()
    return JSONResponse(
        status_code=200,
        content={"message": f"Thread {thread_id} removed successfully."},
    )
