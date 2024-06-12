from datetime import datetime
import enum
import uuid
from sqlalchemy import ARRAY, UUID, Boolean, Column, DateTime, Float, Integer, Numeric, String, ForeignKey, Table, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

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

class OTP(Base):
    __tablename__ = "otp"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String)
    user_id = Column(String(36), ForeignKey('users.id'))
    created_at = Column(DateTime, index=True, default=datetime.now)
    deleted_at = Column(DateTime)
    updated_at = Column(DateTime)
    status = Column(Enum(EntityStatus), nullable=True)

    # Relationships
    user = relationship("User", uselist=False, backref="otp")

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

    id = Column(String, primary_key=True)
    thread_id = Column(String, ForeignKey('threads.id'))
    sender = Column(String)
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    thread = relationship("Thread", back_populates="messages")


class Thread(Base):
    __tablename__ = "threads"

    id = Column(String, primary_key=True)
    messages = relationship("Message", back_populates="thread")

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
    

