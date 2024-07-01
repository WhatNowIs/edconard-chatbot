from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncEngine

Base = declarative_base()

class Datasource:
    def __init__(self):
        self.engine = None
        self.session = None

    def create_session(self):
        Session = sessionmaker(bind=self.engine)
        return Session()

    def bind_models_to_engine(self, base):
        base.metadata.bind = self.engine

    async def close_connection(self):
        if isinstance(self.engine, AsyncEngine):
            await self.engine.dispose()
        else:
            self.engine.dispose()