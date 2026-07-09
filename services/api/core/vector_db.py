from qdrant_client import QdrantClient
from typing import Optional
from services.api.core.config import settings
from services.api.core.logging import logger

class QdrantManager:
    def __init__(self):
        self.client: Optional[QdrantClient] = None

    def connect(self):
        try:
            self.client = QdrantClient(
                host=settings.QDRANT_HOST,
                port=settings.QDRANT_PORT
            )
            # Check connection using a fast operation
            self.client.get_collections()
            logger.info("Successfully established Qdrant connection and verified collections API.")
        except Exception as e:
            logger.error(f"Qdrant connection failed: {e}")
            raise e

    def disconnect(self):
        if self.client:
            # QdrantClient automatically manages closing connection pool
            self.client = None
            logger.info("Closed Qdrant client connection.")

    def check_health(self) -> bool:
        if not self.client:
            return False
        try:
            # Call simple collections check as healthcheck
            self.client.get_collections()
            return True
        except Exception as e:
            logger.error(f"Qdrant health check failed: {e}")
            return False

qdrant_client = QdrantManager()
