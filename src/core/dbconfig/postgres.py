from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from dbconfig.datasource import Datasource

class PostgresDatasource(Datasource):
    def __init__(self, db_uri, base=None):
        super().__init__()
        self.db_uri = db_uri
        self.base = base
        self.engine = self.create_connection()

        if self.base is not None:
            self.bind_models_to_engine(self.base)

        self.session = self.create_session()

    def create_connection(self):
        try:
            engine = create_async_engine(self.db_uri) if self.db_uri.startswith("postgresql+asyncpg") else create_engine(self.db_uri)
            return engine
        except Exception as e:
            raise Exception(f"Error creating connection: {e}")

    async def close_connection(self):
        if isinstance(self.engine, AsyncEngine):
            await self.engine.dispose()
        else:
            self.engine.dispose()