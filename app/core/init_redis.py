from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from app.core.config import redis

async def init_redis():
    client = redis.get_client()
    FastAPICache.init(RedisBackend(client))