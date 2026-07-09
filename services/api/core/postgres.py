import asyncpg
from typing import Optional
from services.api.core.config import settings
from services.api.core.logging import logger

class PostgresManager:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        try:
            self.pool = await asyncpg.create_pool(
                settings.POSTGRES_URL,
                min_size=5,
                max_size=20
            )
            logger.info("Successfully established PostgreSQL connection pool.")
        except Exception as e:
            logger.error(f"PostgreSQL connection failed: {e}")
            raise e

    async def disconnect(self):
        if self.pool:
            await self.pool.close()
            logger.info("Closed PostgreSQL connection pool.")

    async def check_health(self) -> bool:
        if not self.pool:
            return False
        try:
            async with self.pool.acquire() as conn:
                val = await conn.fetchval("SELECT 1")
                return val == 1
        except Exception as e:
            logger.error(f"PostgreSQL health check failed: {e}")
            return False

postgres_client = PostgresManager()
