import redis.asyncio as redis
from datasource import Datasource

class RedisDatasource(Datasource):
    def __init__(self, uri):
        super().__init__()
        self.uri = uri
        self.redis_client = None

    async def get_client(self):
        if self.redis_client is None:
            self.redis_client = redis.from_url(self.uri, encoding="utf-8", decode_responses=True)
        return self.redis_client

    def close_connection(self):
        if self.redis_client:
            self.redis_client.close()