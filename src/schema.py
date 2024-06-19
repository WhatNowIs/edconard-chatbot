from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from enum import Enum

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
    sender : str
    content : str
    timestamp : str


class ResponseThread(BaseModel):
    id : str
    messages : List[ResponseMessage]

class UserModel(BaseModel):
    id: Optional[str] = None
    first_name: str
    last_name: str
    email: str
    phone_number: str
    sex: Optional[str] = None
    status: Optional[str] = 'Pending'
    role_id: Optional[str] = None
    created_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

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