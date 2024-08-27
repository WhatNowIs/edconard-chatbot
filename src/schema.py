import enum
from typing import Any, List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from enum import Enum

class EntityStatusEnum(str, enum.Enum):
    Active = "Active"
    Inactive = "Inactive"
    Deleted = "Deleted"
    Blocked = "Blocked"
    Pending = "Pending"
    Used = "Used"

class EmailTypeEnum(Enum):
    ACCOUNT_VERIFICATION = "account_verification"
    RESET_PASSWORD = "reset_password"
    WELCOME_EMAIL = "welcome_email"
    NEWSLETTER = "newsletter"
    PROMOTIONAL = "promotional"
    PASSWORD_UPDATE = "password_update"

class ResponseMessage(BaseModel):
    id : str
    thread_id : str
    user_id : str
    role : str
    content : str
    annotations: Optional[List[dict]] = None

    class Config:
        from_attributes = True


class ResponseThread(BaseModel):
    id : str 
    user_id : str
    workspace_id: Optional[str] = None
    title : str
    
    class Config:
        from_attributes = True

class ThreadCreate(BaseModel):
    title: str
    workspace_id: str
    user_id: str

class ThreadUpdate(BaseModel):
    title: str
    workspace_id: str
    user_id: str

class ChatMode(BaseModel):
    is_research_exploration: bool

class RefreshBody(BaseModel):
    refresh_token: str

class RoleModel(BaseModel):
    id: str
    name: str
    description: str
    refresh_token: str

    
class UserModel(BaseModel):
    id: Optional[str] = None
    first_name: str
    last_name: str
    email: str
    phone_number: str
    sex: Optional[str] = None
    status: Optional[str] = 'Pending'
    role_id: Optional[str] = None
    role: Optional[RoleModel] = None
    created_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class DeactivateResponse(BaseModel):
    block_user: bool
    data: Optional[UserModel] = None 

class UpdateUserRole(BaseModel):
    role: str

class UserCreateModel(BaseModel):
    password: str
    user_data: UserModel

class UserSinginModel(BaseModel):
    password: str
    email: str

class VerifyOtp(BaseModel):    
    email: EmailStr
    code: str
    otp_type: EmailTypeEnum

class ResetPassword(BaseModel):    
    email: EmailStr


class UpdatePassword(BaseModel):    
    password: str
    email: EmailStr
    
class SetArticleData(BaseModel):    
    document_link: str
    order: int

class Document(BaseModel):
    title: str
    content: Optional[List[Any]] = None
    inline_objects: Optional[Any] = None

class DocumentResponse(BaseModel):
    headline: str
    authors: str
    publication: str
    summary: str
    order_of_appearance: str

class ChangePassword(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

class WorkspaceCreate(BaseModel):
    name: str

class Workspace(BaseModel):
    id: str
    name: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    status: Optional[str] = None

    class Config:
        from_attributes = True

class _Message(BaseModel):
    role: str
    content: str

class _UpdateChat(BaseModel):
    messages: List[_Message]
    thread_id: str