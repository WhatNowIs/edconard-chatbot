import redis.asyncio as redis
from src.core.dbconfig.datasource import Datasource
from src.llm.env_config import get_config
from redis.asyncio.client import Redis

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
REDIS_URL = get_config().redis_url

redis_db = RedisDatasource(uri=REDIS_URL)

# Dependency to get DB session
async def get_redis_client() -> Redis:
    return await redis_db.get_client()
