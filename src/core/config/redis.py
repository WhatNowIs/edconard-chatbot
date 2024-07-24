import os
from pathlib import Path
from dotenv import load_dotenv
import redis.asyncio as redis
from src.core.config.datasource import Datasource
from redis.asyncio.client import Redis

current_file = Path(__file__).resolve()
root_directory = current_file.parents[3]  

env_path = root_directory / 'config' / '.env'
load_dotenv(dotenv_path=env_path)

class RedisDatasource(Datasource):
    def __init__(self, uri):
        super().__init__()
        self.uri = uri
        self.redis_client = None

    async def get_client(self) -> Redis:
        if self.redis_client is None:
            self.redis_client = redis.from_url(self.uri, encoding="utf-8", decode_responses=True)
        return self.redis_client

    def close_connection(self):
        if self.redis_client:
            self.redis_client.close()

# Initialize the database connection
REDIS_URL = os.getenv('REDIS_URL')

redis_db = RedisDatasource(uri=REDIS_URL)

# Dependency to get DB session
async def get_redis_client() -> Redis:
    return await redis_db.get_client()
