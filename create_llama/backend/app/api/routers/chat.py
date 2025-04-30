from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio
from typing import List, Any, Optional, Dict, Tuple, Union
from fastapi import APIRouter, Depends, HTTPException, Request, status
from llama_index.core.chat_engine.types import BaseChatEngine
from llama_index.core.schema import NodeWithScore
from llama_index.core.llms import ChatMessage, MessageRole
from sqlalchemy.ext.asyncio import AsyncSession
from create_llama.backend.app.engine import get_chat_engine
from create_llama.backend.app.api.routers.vercel_response import VercelStreamResponse
from create_llama.backend.app.api.routers.messaging import EventCallbackHandler
from aiostream import stream
from src.app.routers.auth.accounts import get_session
from src.core.config.postgres import get_db
from src.core.config.redis import get_redis_client
from src.core.models.base import Message
from src.core.services.message import MessageService
from src.core.services.thread import ThreadService
from src.core.services.user import UserService 
from redis.asyncio.client import Redis
from create_llama.backend.app.utils.helpers import Article, get_document_by_url

from src.schema import _UpdateChat, ChatMode, ResponseMessage, SetArticleData
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

class MacroRoundup(BaseModel):
    headline: str
    publisher: str
    summary: str
    authors: str

class MacroRoundupList(BaseModel):
    article: List[MacroRoundup]

class MacroRoundupResponse(BaseModel):
    related_articles: str

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

    messages = [
        ChatMessage(
            role=m.role,
            content=m.content,
        )
        for m in data.messages
    ]
    return last_message.content, messages

@r.post("/search", response_model=Union[MacroRoundupResponse, List[MacroRoundupResponse]])
async def search(
    data: Union[MacroRoundup, MacroRoundupList],
    chat_engine: BaseChatEngine = Depends(get_chat_engine),
):

    if isinstance(data, MacroRoundup):
        query = f"""
        Find related articles for the article with the following headline and summary.
        
        #Article Headline
        {data.headline}
        #Article Summary
        {data.summary}
        """
        
        response = await chat_engine.achat(query, chat_history=[])

        return MacroRoundupResponse(
            related_articles=response.response,
        )
    elif isinstance(data, MacroRoundupList):
        # Prepare queries for each article
        queries = [
            f"""
            Find related articles for the article with the following headline and summary.

            #Article Headline
            {article.headline}
            #Article Summary
            {article.summary}
            """
            for article in data.article
        ]

        # Run all chat_engine.achat() calls in parallel
        responses = await asyncio.gather(
            *[chat_engine.achat(query, chat_history=[]) for query in queries]
        )
    
        # Process responses as needed (example: return a list of results)
        return [
            MacroRoundupResponse(
                related_articles=response.response,
            )
            for response in responses
        ]
    
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
async def chat_thread(
    thread_id: str,
    request: Request,
    data: _ChatData,
    session: dict = Depends(get_session),
    thread_service: ThreadService = Depends(get_thread_service),
    message_service: MessageService = Depends(get_message_service),
    # user_service: UserService = Depends(get_user_service),
    # redis_client: Redis = Depends(get_redis_client)
):    
    last_message_content, messages = await parse_chat_data(data)

    if "sub" in session:
        user_id = session["sub"]

        messages_tmp: List[Message] = await thread_service.get_messages_by_thread_id(thread_id=thread_id, uid=user_id)
            
        new_message = Message(
            thread_id=thread_id,
            user_id=user_id,
            role=MessageRole.USER.value,
            content=last_message_content
        )
        
        # Await the tasks to ensure they complete
        await message_service.create(new_message)

        messages = [ChatMessage(content=message.content, role=MessageRole.USER if str(message.role) == "user" else MessageRole.ASSISTANT) for message in messages_tmp]
        
        chat_engine = await get_chat_engine()

        event_handler = EventCallbackHandler()
        chat_engine.callback_manager.handlers.append(event_handler)
        
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
async def chat_mode_request(
    user_id: str,
    data: ChatMode,
    session: dict = Depends(get_session),    
    redis_client: Redis = Depends(get_redis_client),
    user_service: UserService = Depends(get_user_service),
):
    
    if "sub" in session and user_id == session["sub"]:

        get_logger().info(f"chat mode sent: {data.is_research_exploration}")
    
        await user_service.update_chat_mode(user_id, data.is_research_exploration, redis_client)
    
        return JSONResponse(status_code=200, content={"message": f"Successfully switched to {data.is_research_exploration} mode."})
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid session",
        headers={"WWW-Authenticate": "Bearer"},
    )
# non-streaming endpoint - delete if not needed
@r.patch("")
async def add_chat_messages(
    data: _UpdateChat,
    session: dict = Depends(get_session),    
    redis_client: Redis = Depends(get_redis_client),
    user_service: UserService = Depends(get_user_service),
    message_service: MessageService = Depends(get_message_service),
):
    
    if "sub" in session:
        user_id = session["sub"]
        
        article = await  user_service.get_article(user_id=user_id, redis_client=redis_client)
        responses = []
        for message in data.messages:
            new_message = Message(
                thread_id=data.thread_id,
                user_id=user_id,
                role=MessageRole.ASSISTANT.value if MessageRole.ASSISTANT.value == message.role else MessageRole.USER.value,
                content=message.content,
                annotations=[{
                    "url": article.url,
                    "order": article.order,
                    "headline": article.headline,
                    "is_research_exploration": False
                }]
            )
            created_obj = await message_service.create(new_message)
            responses.append(ResponseMessage.model_validate(created_obj))
    
        return responses
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid session",
        headers={"WWW-Authenticate": "Bearer"},
    )

# non-streaming endpoint - delete if not needed
@r.get("/chat-mode/{user_id}")
async def get_chat_mode(
    user_id: str,
    session: dict = Depends(get_session),    
    redis_client: Redis = Depends(get_redis_client),
    user_service: UserService = Depends(get_user_service),
):
    
    if "sub" in session and user_id == session["sub"]:
    
        chat_mode = await user_service.get_chat_mode(user_id, redis_client)

        get_logger().info(f"retrieved chat mode: {chat_mode}")
    
        return JSONResponse(status_code=200, content={"mode": chat_mode}) 
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid session",
        headers={"WWW-Authenticate": "Bearer"},
    )

# non-streaming endpoint - delete if not needed
@r.post("/article")
async def update_article(
    data: SetArticleData,
    session: dict = Depends(get_session),    
    redis_client: Redis = Depends(get_redis_client),
    user_service: UserService = Depends(get_user_service),
) -> Article:
    
    if "sub" in session:
        user_id = session['sub']
        documents = await get_document_by_url(data.document_link)

        doc = [document for document in documents if int(document.order_of_appearance) == data.order]

        if len(doc) == 0:            
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order of appearance is out bound",
            )
        else:
            doc = doc[0]


        article = Article(
            abstract=doc.summary,
            authors=doc.authors,
            headline=doc.headline,
            publisher=doc.publication,
            order=data.order,
            url=data.document_link
        )
        result = await user_service.update_article(user_id, article, redis_client)

        get_logger().info(f"Updated article data with order {data.order}")

        if result != None:
    
            return result

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid session",
        headers={"WWW-Authenticate": "Bearer"},
    )

# non-streaming endpoint - delete if not needed
@r.get("/article")
async def get_article(
    session: dict = Depends(get_session),    
    redis_client: Redis = Depends(get_redis_client),
    user_service: UserService = Depends(get_user_service),
) -> Article:
    
    if "sub" in session:
        user_id = session['sub']

        article = await user_service.get_article(user_id=user_id, redis_client=redis_client)
    
        return article

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid session",
        headers={"WWW-Authenticate": "Bearer"},
    )
