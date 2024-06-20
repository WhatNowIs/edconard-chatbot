from typing import Any, List
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.controllers.threads import ThreadManager
from src.schema import ResponseThread, Thread
from src.core.dbconfig import get_db

threads_router = r = APIRouter()

@r.get("")
async def fetch_threads(db: AsyncSession = Depends(get_db)) -> List[ResponseThread]:
    return await ThreadManager.get_all_threads(db)

@r.post("")
async def create_thread(thread: Thread, db: AsyncSession = Depends(get_db)) -> ResponseThread:
    return await ThreadManager.create_thread(db, thread)

@r.delete("/{thread_id}")
async def remove_thread(thread_id: str, db: AsyncSession = Depends(get_db)):
    await ThreadManager.remove_thread(db, thread_id)
    return JSONResponse(
        status_code=200,
        content={"message": f"Thread {thread_id} removed successfully."},
    )
