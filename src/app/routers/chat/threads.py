from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.routers.auth.accounts import get_session
from src.core.dbconfig.postgres import get_db
from src.core.models.base import Thread
from src.core.services.thread import ThreadService
from src.schema import ResponseMessage, ResponseThread, ThreadCreate, ThreadUpdate

threads_router = r = APIRouter()

def get_thread_service(db: AsyncSession = Depends(get_db)) -> ThreadService:
    return ThreadService(db)

@r.post("")
async def create_thread(
    data: ThreadCreate,
    session: dict = Depends(get_session),
    thread_service: ThreadService = Depends(get_thread_service)
):
    if "sub" in session:
        user_id = session["sub"]
        thread = Thread(
            user_id = user_id,
            title = data.title,
        )
        created_thread = await thread_service.create(thread)   

        return ResponseThread(**created_thread.to_dict())
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authorized to access threads",
    )

@r.get("")
async def fetch_threads(    
    session: dict = Depends(get_session),
    thread_service: ThreadService = Depends(get_thread_service)
) -> List[ResponseThread]:        
    if "sub" in session:
        user_id = session["sub"]

        threads = await thread_service.get_all_by_user_id(user_id)

        return [ResponseThread(**thread.to_dict()) for thread in threads]
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authorized to access threads",
    )

@r.patch("/{thread_id}", response_model=ResponseThread)
async def update_thread(
    thread_id: str,
    data: ThreadUpdate,
    session: dict = Depends(get_session),
    thread_service: ThreadService = Depends(get_thread_service)
):    
    if "sub" in session:
        thread = await thread_service.get_by_user_id_and_thread_id(uid=data.user_id, thread_id=thread_id)

        if(thread):
            thread.title = data.title
            await thread_service.update(thread_id, thread)
            
            return ResponseThread(**thread.to_dict())
        else:
            print("Thread not found")

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authorized to access this thread",
    )

@r.get("/{thread_id}", response_model=ResponseThread)
async def get_thread(
    thread_id: str, 
    session: dict = Depends(get_session),
    thread_service: ThreadService = Depends(get_thread_service)
):    
    if "sub" in session:
        user_id = session["sub"]
        thread = await thread_service.get_by_user_id_abd_thread_id(uid=user_id, thread_id=thread_id)
        return thread

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authorized to access this thread",
    )

@r.get("/messages/{thread_id}")
async def get_messages_by_thread_id(
    thread_id: str, 
    session: dict = Depends(get_session),
    thread_service: ThreadService = Depends(get_thread_service)
):    
    if "sub" in session:
        user_id = session["sub"]
        messages = await thread_service.get_messages_by_thread_id(uid=user_id, thread_id=thread_id)
        reponse_messages = [ResponseMessage(**message.to_dict()) for message in messages]        
        return reponse_messages

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authorized to access threads",
    )

@r.delete("/{thread_id}")
async def remove_thread(
    thread_id: str, 
    session: dict = Depends(get_session),
    thread_service: ThreadService = Depends(get_thread_service)
):    
    if "sub" in session:
        user_id = session["sub"]
        thread = await thread_service.get_by_user_id(user_id)

        if thread is not None and thread.id == thread_id:
            await thread_service.delete(thread_id)
            return JSONResponse(
                status_code=200,
                content={"message": f"Thread {thread_id} removed successfully."},
            )                    
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized to delete this thread",
        )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authorized to access threads",
    )
