from typing import List
from pydantic import BaseModel


class ResponseMessage(BaseModel):
    id : str
    conversation_thread_id : str
    sender : str
    content : str
    timestamp : str


class ResponseConversationThread(BaseModel):
    id : str
    messages : List[ResponseMessage]