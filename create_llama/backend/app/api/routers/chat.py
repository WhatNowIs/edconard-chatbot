from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List, Any, Optional, Dict, Tuple
from fastapi import APIRouter, Depends, HTTPException, Request, status
from llama_index.core.chat_engine.types import BaseChatEngine
from llama_index.core.schema import NodeWithScore
from llama_index.core.llms import ChatMessage, MessageRole
from sqlalchemy.ext.asyncio import AsyncSession
from app.engine import get_chat_engine
from app.api.routers.vercel_response import VercelStreamResponse
from app.api.routers.messaging import EventCallbackHandler
from aiostream import stream
from src.app.routers.auth.accounts import get_session
from src.core.dbconfig.postgres import get_db
from src.core.dbconfig.redis import get_redis_client
from src.core.models.base import Message
from src.core.services.message import MessageService
from src.core.services.thread import ThreadService
from src.core.services.user import UserService 
from redis.asyncio.client import Redis

from src.schema import ChatMode
from src.utils.logger import get_logger

chat_router = r = APIRouter()

def get_message_service(db: AsyncSession = Depends(get_db)) -> MessageService:
    return MessageService(db)

def get_thread_service(db: AsyncSession = Depends(get_db)) -> ThreadService:
    return ThreadService(db)

def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)

class _Message(BaseModel):
    role: MessageRole
    content: str


class _ChatData(BaseModel):
    messages: List[_Message]

    class Config:
        json_schema_extra = {
            "example": {
                "messages": [
                    {
                        "role": "user",
                        "content": "What standards for letters exist?",
                    }
                ]
            }
        }


class _SourceNodes(BaseModel):
    id: str
    metadata: Dict[str, Any]
    score: Optional[float]
    text: str

    @classmethod
    def from_source_node(cls, source_node: NodeWithScore):
        return cls(
            id=source_node.node.node_id,
            metadata=source_node.node.metadata,
            score=source_node.score,
            text=source_node.node.text,  # type: ignore
        )

    @classmethod
    def from_source_nodes(cls, source_nodes: List[NodeWithScore]):
        return [cls.from_source_node(node) for node in source_nodes]


class _Result(BaseModel):
    result: _Message
    nodes: List[_SourceNodes]


async def parse_chat_data(data: _ChatData) -> Tuple[str, List[ChatMessage]]:
    # check preconditions and get last message
    if len(data.messages) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No messages provided",
        )
    last_message = data.messages.pop()
    if last_message.role != MessageRole.USER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Last message must be from user",
        )
    # convert messages coming from the request to type ChatMessage
    messages = [
        ChatMessage(
            role=m.role,
            content=m.content,
        )
        for m in data.messages
    ]
    return last_message.content, messages


# streaming endpoint - delete if not needed
@r.post("")
async def chat(
    request: Request,
    data: _ChatData,
    chat_engine: BaseChatEngine = Depends(get_chat_engine),
):
    last_message_content, messages = await parse_chat_data(data)

    event_handler = EventCallbackHandler()
    chat_engine.callback_manager.handlers.append(event_handler)  # type: ignore
    response = await chat_engine.astream_chat(last_message_content, messages)

    async def content_generator():
        # Yield the text response
        async def _text_generator():
            async for token in response.async_response_gen():
                yield VercelStreamResponse.convert_text(token)
            # the text_generator is the leading stream, once it's finished, also finish the event stream
            event_handler.is_done = True

        # Yield the events from the event handler
        async def _event_generator():
            async for event in event_handler.async_event_gen():
                event_response = event.to_response()
                if event_response is not None:
                    yield VercelStreamResponse.convert_data(event_response)

        combine = stream.merge(_text_generator(), _event_generator())
        async with combine.stream() as streamer:
            async for item in streamer:
                if await request.is_disconnected():
                    break
                yield item

        # Yield the source nodes
        yield VercelStreamResponse.convert_data(
            {
                "type": "sources",
                "data": {
                    "nodes": [
                        _SourceNodes.from_source_node(node).dict()
                        for node in response.source_nodes
                    ]
                },
            }
        )

    return VercelStreamResponse(content=content_generator())


# streaming endpoint - delete if not needed
@r.post("/{thread_id}/message")
async def chat(
    thread_id: str,
    request: Request,
    data: _ChatData,
    session: dict = Depends(get_session),
    thread_service: ThreadService = Depends(get_thread_service),
    chat_engine: BaseChatEngine = Depends(get_chat_engine),
    message_service: MessageService = Depends(get_message_service)
):    
    # session: dict = await get_session()
    last_message_content, messages = await parse_chat_data(data)

    if "sub" in session:
        user_id = session["sub"]
        messages_tmp: List[Message] = await thread_service.get_messages_by_thread_id(thread_id=thread_id, uid=user_id)
        messages = [ChatMessage(content=last_message_content, role=message.role) for message in messages_tmp]        
     
        new_message = Message(
            thread_id=thread_id,
            user_id=user_id,
            role=MessageRole.USER.value,
            content=last_message_content
        )

        await message_service.create(new_message)

        event_handler = EventCallbackHandler()
        chat_engine.callback_manager.handlers.append(event_handler)  # type: ignore
        response = await chat_engine.astream_chat(last_message_content, messages)
        
        tmp_message_container = [""]
        sources = []
        events = []

        async def content_generator():
            # Yield the text response
            async def _text_generator():
                async for token in response.async_response_gen():
                    msg = VercelStreamResponse.convert_text(token)
                    tmp_message_container[0] += token

                    yield msg
                    # yield VercelStreamResponse.convert_text(token)
                # the text_generator is the leading stream, once it's finished, also finish the event stream
                event_handler.is_done = True


            # Yield the events from the event handler
            async def _event_generator():
                async for event in event_handler.async_event_gen():
                    event_response = event.to_response()
                    if event_response is not None:
                        events.append(event_response)

                        yield VercelStreamResponse.convert_data(event_response)

            combine = stream.merge(_text_generator(), _event_generator())
            async with combine.stream() as streamer:
                async for item in streamer:
                    if await request.is_disconnected():
                        break
                    yield item

            source = {
                "type": "sources",
                "data": {
                    "nodes": [
                        _SourceNodes.from_source_node(node).dict()
                        for node in response.source_nodes
                    ]
                },
            }

            sources.append(source)
            # Yield the source nodes
            yield VercelStreamResponse.convert_data(source)
        
            if event_handler.is_done:
                new_message = Message(
                    thread_id=thread_id,
                    user_id=user_id,
                    role=MessageRole.ASSISTANT.value,
                    content=tmp_message_container[0],
                    annotations=events + sources
                )
                await message_service.create(new_message)


        return VercelStreamResponse(content=content_generator())
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authorized to access threads",
    )

# non-streaming endpoint - delete if not needed
@r.post("/request")
async def chat_request(
    data: _ChatData,
    chat_engine: BaseChatEngine = Depends(get_chat_engine),
) -> _Result:
    last_message_content, messages = await parse_chat_data(data)

    response = await chat_engine.achat(last_message_content, messages)
    return _Result(
        result=_Message(role=MessageRole.ASSISTANT, content=response.response),
        nodes=_SourceNodes.from_source_nodes(response.source_nodes),
    )


# non-streaming endpoint - delete if not needed
@r.patch("/chat-mode/{user_id}")
async def chat_request(
    user_id: str,
    data: ChatMode,
    session: dict = Depends(get_session),    
    redis_client: Redis = Depends(get_redis_client),
    user_service: UserService = Depends(get_user_service),
):
    
    if "sub" in session and user_id == session["sub"]:

        get_logger().info(f"chat mode sent: {data.mode}")
    
        await user_service.update_chat_mode(user_id, data.mode, redis_client)
    
        return JSONResponse(status_code=200, content={"message": f"Successfully switched to {data.mode.replace('-', ' ')} mode."})
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid session",
        headers={"WWW-Authenticate": "Bearer"},
    )

# non-streaming endpoint - delete if not needed
@r.get("/chat-mode/{user_id}")
async def chat_request(
    user_id: str,
    session: dict = Depends(get_session),    
    redis_client: Redis = Depends(get_redis_client),
    user_service: UserService = Depends(get_user_service),
) -> _Result:
    
    if "sub" in session and user_id == session["sub"]:
    
        chat_mode = await user_service.get_chat_mode(user_id, redis_client)

        get_logger().infor(f"retrieved chat mode: {chat_mode}")
    
        return JSONResponse(status_code=200, content={"mode": chat_mode})

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid session",
        headers={"WWW-Authenticate": "Bearer"},
    )
