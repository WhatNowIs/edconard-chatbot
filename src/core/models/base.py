from datetime import datetime
import random
from datetime import datetime, timedelta
import enum
import uuid
from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, Table, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from src.utils.logger import get_logger

Base = declarative_base()

def get_otp_expiration(minutes: int = 10) -> datetime:
    expiration_time = datetime.now() + timedelta(minutes=minutes)
    return expiration_time

def generate_otp() -> str:
    otp = random.randint(100000, 999999)
    return str(otp)

class EntityStatus(enum.Enum):
    Active = "Active"
    Inactive = "Inactive"
    Deleted = "Deleted"
    Blocked = "Blocked"
    Pending = "Pending"
    Used = "Used"

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

    # Functions
    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

class Role(Base):
    __tablename__ = "roles"
    id = Column(String, primary_key=True)
    name = Column(String)
    description = Column(String)

    # Relationships
    users = relationship("User", backref="role")

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

# class OTP(Base):
#     __tablename__ = "otp"
#     id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
#     code = Column(String)
#     user_id = Column(String(36), ForeignKey('users.id'))
#     created_at = Column(DateTime, index=True, default=datetime.now)
#     deleted_at = Column(DateTime)
#     updated_at = Column(DateTime)
#     status = Column(Enum(EntityStatus), nullable=True)

#     # Relationships
#     user = relationship("User", uselist=False, backref="otp")

#     def to_dict(self):
#         return {column.name: getattr(self, column.name) for column in self.__table__.columns}

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

    id = Column(String, primary_key=True)
    thread_id = Column(String, ForeignKey('threads.id'))
    sender = Column(String)
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    thread = relationship("Thread", back_populates="messages")
    
    # Functions
    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class Thread(Base):
    __tablename__ = "threads"

    id = Column(String, primary_key=True)
    messages = relationship("Message", back_populates="thread")

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
    code = Column(String, default=generate_otp())
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
