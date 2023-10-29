from typing import Optional
from redis.asyncio import Redis

from src.core.config import settings


redis: Optional[Redis] = None
redis.redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)


async def get_redis() -> Redis:
    return redis
