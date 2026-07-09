import redis.asyncio as aioredis
from typing import Optional
from services.api.core.config import settings
from services.api.core.logging import logger

class RedisManager:
    def __init__(self):
        self.client: Optional[aioredis.Redis] = None

    async def connect(self):
        try:
            self.client = aioredis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=0,
                decode_responses=True
            )
            await self.client.ping()
            logger.info("Successfully established Redis client and verified connection.")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            raise e

    async def disconnect(self):
        if self.client:
            await self.client.close()
            logger.info("Closed Redis connection.")

    async def check_health(self) -> bool:
        if not self.client:
            return False
        try:
            return await self.client.ping()
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False

redis_client = RedisManager()
