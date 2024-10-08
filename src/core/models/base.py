from datetime import datetime
import json
import random
from datetime import datetime, timedelta
import enum
import uuid
from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, Table, Enum, JSON, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


from src.utils.logger import get_logger

Base = declarative_base()

def get_otp_expiration(minutes: int = 10) -> datetime:
    expiration_time = datetime.now() + timedelta(minutes=minutes)
    return expiration_time

class OTPGenerator:
    def __init__(self):
        self.otps = random.sample(range(100000, 1000000), 900000)
        self.index = 0

    def generate_unique_otp(self) -> str:
        if self.index >= len(self.otps):
            raise ValueError("All possible OTPs have been generated.")
        otp = self.otps[self.index]
        self.index += 1
        return str(otp)
    
class UserRole(enum.Enum):
    SUPER_ADMIN = "Super Admin"
    ADMIN = "Admin"
    EDITOR = "Editor"
    USER = "User"

class EntityStatus(enum.Enum):
    Active = "Active"
    Inactive = "Inactive"
    Deleted = "Deleted"
    Blocked = "Blocked"
    Pending = "Pending"
    Used = "Used"
# Role description
role_descriptions = {
    UserRole.SUPER_ADMIN: "Has access to all system features, including user management and system configuration.",
    UserRole.ADMIN: "Can manage most aspects of the system but has some restrictions on critical operations.",
    UserRole.EDITOR: "Can create and manage content, but cannot manage users or system settings.",
    UserRole.USER: "Can view and interact with content but has no administrative privileges.",
}
# Association Tables
tenant_users = Table(
    'tenant_users', Base.metadata,
    Column('user_id', String(36), ForeignKey('users.id')),
    Column('tenant_id', String(36), ForeignKey('tenants.id'))
)

user_addresses = Table(
    'user_addresses', Base.metadata,
    Column('user_id', String(36), ForeignKey('users.id')),
    Column('address_id', String(36), ForeignKey('addresses.id'))
)

tenant_addresses = Table(
    'tenant_addresses', Base.metadata,
    Column('tenant_id', String(36), ForeignKey('tenants.id')),
    Column('address_id', String(36), ForeignKey('addresses.id'))
)

workspace_users = Table(
    'workspace_users', Base.metadata,
    Column('user_id', String(36), ForeignKey('users.id')),
    Column('workspace_id', String(36), ForeignKey('workspaces.id'))
)
# Models

class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = Column(String)
    last_name = Column(String)
    sex = Column(String)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String)
    created_at = Column(DateTime, index=True, default=datetime.now)
    deleted_at = Column(DateTime)
    updated_at = Column(DateTime)
    status = Column(Enum(EntityStatus), nullable=True)
    role_id = Column(String, ForeignKey('roles.id'))

    # Relationships  

    addresses = relationship("Address", secondary=user_addresses, backref="users")
    tenants = relationship("Tenant", secondary=tenant_users, backref="users")
    messages = relationship("Message", back_populates="user")
    threads = relationship("Thread", back_populates="user")
    workspaces = relationship("Workspace", secondary=workspace_users, back_populates="users")
    role = relationship("Role")


    # Functions
    def to_dict(self):
        user_dict = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        user_dict['role'] = self.role.to_dict() if self.role else None
        return user_dict

class Role(Base):
    __tablename__ = "roles"
    id = Column(String, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)

    # Relationships
    
    # users = relationship("User")

    # Functions
    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

class Credential(Base):
    __tablename__ = "credentials"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'))
    password = Column(String)
    salt = Column(String)
    created_at = Column(DateTime, index=True, default=datetime.now)
    deleted_at = Column(DateTime)
    updated_at = Column(DateTime)
    status = Column(Enum(EntityStatus), nullable=True)

    # Relationships
    user = relationship("User", uselist=False, backref="credential")

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

class Address(Base):
    __tablename__ = "addresses"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    country = Column(String)
    province = Column(String)
    city = Column(String)
    postal = Column(String)
    physical = Column(String)
    created_at = Column(DateTime, index=True, default=datetime.now)
    deleted_at = Column(DateTime)
    updated_at = Column(DateTime)
    status = Column(Enum(EntityStatus), nullable=True)

    # Functions
    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    thread_id = Column(String, ForeignKey('threads.id'))
    user_id = Column(String, ForeignKey('users.id'))
    role = Column(String)
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    annotations = Column(ARRAY(JSON), nullable=True)

    thread = relationship("Thread", back_populates="messages")
    user = relationship("User", back_populates="messages")
    
    # Functions
    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

class Thread(Base):
    __tablename__ = "threads"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.id'))
    workspace_id = Column(String(36), ForeignKey('workspaces.id'))
    title =  Column(String)

    messages = relationship("Message", back_populates="thread")
    user = relationship("User", back_populates="threads")
    workspace = relationship("Workspace", back_populates="threads")

    # Functions
    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    created_at = Column(DateTime, index=True, default=datetime.now)
    deleted_at = Column(DateTime)
    updated_at = Column(DateTime)
    status = Column(Enum(EntityStatus), nullable=True)

    # Relationships
    addresses = relationship("Address", secondary=tenant_addresses, backref="tenants")

    # Functions
    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

class EmailType(Base):
    __tablename__ = 'email_types'
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, unique=True, index=True)
    
class EmailTemplate(Base):
    __tablename__ = 'email_templates'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    subject = Column(String)
    content = Column(String)

class OTP(Base):
    __tablename__ = "otp"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String, default=OTPGenerator().generate_unique_otp())
    email = Column(String, index=True)
    user_id = Column(String(36), ForeignKey('users.id'))
    email_template_id = Column(Integer, ForeignKey('email_templates.id'))
    email_type_id = Column(Integer, ForeignKey('email_types.id'))
    expires_at = Column(DateTime, default=get_otp_expiration())
    created_at = Column(DateTime, index=True, default=datetime.now())
    deleted_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.now())
    status = Column(Enum(EntityStatus), nullable=True)

    # Relationships
    user = relationship("User", uselist=False, backref="otp")
    email_template = relationship("EmailTemplate")
    email_type = relationship("EmailType")

    # Functions
    def is_expired(self):
        current_time = datetime.now()
        get_logger().info(f"Current time: {current_time}, Expiry time: {self.expires_at}")

        return current_time > self.expires_at

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    created_at = Column(DateTime, index=True, default=datetime.now)
    updated_at = Column(DateTime)
    status = Column(String, nullable=True)

    # Relationships
    users = relationship("User", secondary="workspace_users", back_populates="workspaces")
    threads = relationship("Thread", back_populates="workspace")

    # Functions
    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}