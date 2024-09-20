from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class Message(BaseModel):
    role: str
    content: str
    refusal: Optional[str] = None  # Optional to account for null values

class Choice(BaseModel):
    index: int
    message: Message
    logprobs: Optional[Dict] = None  # logprobs could be a dictionary or None
    finish_reason: str

class CompletionTokensDetails(BaseModel):
    reasoning_tokens: Optional[int] = None  # Define any additional keys expected

class UsageDetails(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    completion_tokens_details: CompletionTokensDetails  # Use a custom model

class Body(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: List[Choice]
    usage: UsageDetails
    system_fingerprint: str

class Response(BaseModel):
    status_code: int
    request_id: str
    body: Body
    error: Optional[str] = None

class BatchResult(BaseModel):
    id: str
    custom_id: str
    response: Response
