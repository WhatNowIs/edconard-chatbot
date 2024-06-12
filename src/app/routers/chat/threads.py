from typing import Any, List
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from src.app.controllers.threads import ThreadManager
from src.schema import ResponseThread


threads_router = r = APIRouter()


@r.get("")
async def fetch_threads() -> List[ResponseThread]:
    """
    Get the current threads.
    """
    return await ThreadManager.get_all_threads()


@r.post("")
async def create_thread() -> ResponseThread | Any:
    """
    Create a new thread.
    """
    res = await ThreadManager.create_thread()
    return res


@r.delete("/{thread_id}")
async def remove_thread(thread_id: str):
    """
    Remove a thread.
    """
    ThreadManager.remove_thread()

    return JSONResponse(
        status_code=200,
        content={"message": f"Thread {thread_id} removed successfully."},
    )
