from fastapi import APIRouter, UploadFile
from fastapi.responses import JSONResponse
from src.core.models.base import Thread
from src.llm.file import File
from src.app.controllers.threads import ThreadManager


threads_router = r = APIRouter()


@r.get("")
def fetch_threads() -> list[File]:
    """
    Get the current threads.
    """
    return ThreadManager.get_all_threads()


@r.post("")
async def create_thread() -> Thread:
    """
    Create a new thread.
    """
    res = await ThreadManager.create_thread()
    return res


@r.delete("/{thread_id}")
def remove_thread(thread_id: str):
    """
    Remove a thread.
    """
    ThreadManager.remove_thread()
    return JSONResponse(
        status_code=200,
        content={"message": f"Thread {thread_id} removed successfully."},
    )
