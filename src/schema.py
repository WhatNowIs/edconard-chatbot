from typing import List
from pydantic import BaseModel


class ResponseMessage(BaseModel):
    id : str
    thread_id : str
    sender : str
    content : str
    timestamp : str


class ResponseThread(BaseModel):
    id : str
    messages : List[ResponseMessage]