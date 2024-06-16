# src/core/dbconfig/connection.py

import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from src.core.dbconfig.datasource import Datasource

class PostgresDatasource(Datasource):
    def __init__(self, db_uri, base=None):
        super().__init__()
        self.db_uri = db_uri
        self.base = base
        self.engine = self.create_connection()

        if self.base is not None:
            self.bind_models_to_engine(self.base)

        self.async_session_maker = self.create_async_session()

    def create_connection(self):
        try:
            if self.db_uri.startswith("postgresql+asyncpg"):
                engine = create_async_engine(self.db_uri)
            else:
                raise Exception("Only asyncpg connection strings are supported for async operations.")
            return engine
        except Exception as e:
            raise Exception(f"Error creating connection: {e}")

    def create_async_session(self):
        return async_sessionmaker(
            self.engine,
            expire_on_commit=False,
            class_=AsyncSession
        )

    async def close_connection(self):
        if isinstance(self.engine, Engine):
            await self.engine.dispose()

    async def get_db(self):
        async with self.async_session_maker() as session:
            yield session

# Initialize the database connection
DATABASE_URL = os.getenv("DB_URI")
database = PostgresDatasource(db_uri=DATABASE_URL)

# Dependency to get DB session
async def get_db():
    async for session in database.get_db():
        yield session
