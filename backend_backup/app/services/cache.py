import aioredis, json, hashlib, asyncio
from ..core.settings import settings

class ContentCache:
    def __init__(self, redis_url: str):
        self.redis = aioredis.from_url(redis_url, decode_responses=True)
        self.lock = asyncio.Lock()

    async def get(self, key: str):
        # TODO: Implement cache retrieval
        return await self.redis.get(key)

    async def set(self, key: str, value: dict, ttl: int = None):
        async with self.lock:
            await self.redis.set(key, json.dumps(value), ex=ttl or settings.CACHE_TTL_SECONDS)

    async def publish(self, channel: str, message: str):
        # TODO: Implement pub/sub for progress updates
        await self.redis.publish(channel, message)

    @staticmethod
    def key(job_id: str, fmt: str, v: int):
        return f"content:{job_id}:{fmt}:{v}" 