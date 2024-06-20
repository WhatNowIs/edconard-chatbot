from typing import Any, List
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.controllers.threads import ThreadManager
from src.core.dbconfig.postgres import get_db
from src.core.models.base import Thread
from src.schema import ResponseThread

threads_router = r = APIRouter()

@r.get("")
async def fetch_threads(db: AsyncSession = Depends(get_db)) -> List[ResponseThread]:
    # threads = await ThreadManager.get_all_threads(db)
    return []

# @r.post("")
# async def create_thread(thread: Thread, db: AsyncSession = Depends(get_db)) -> ResponseThread:
#     new_thread = await ThreadManager.create_thread(db, thread)
#     return ResponseThread(**new_thread.to_dict())

# @r.delete("/{thread_id}")
# async def remove_thread(thread_id: str, db: AsyncSession = Depends(get_db)):
#     await ThreadManager.remove_thread(db, thread_id)
#     return JSONResponse(
#         status_code=200,
#         content={"message": f"Thread {thread_id} removed successfully."},
#     )
