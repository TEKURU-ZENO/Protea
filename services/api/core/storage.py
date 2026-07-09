import boto3
from botocore.client import Config
from typing import Optional, Any
from services.api.core.config import settings
from services.api.core.logging import logger

class StorageManager:
    def __init__(self):
        self.s3_client: Optional[Any] = None

    def connect(self):
        try:
            # We connect to MinIO in dev, AWS S3 in prod
            endpoint = f"http://{settings.MINIO_ENDPOINT}" if not settings.MINIO_SECURE else f"https://{settings.MINIO_ENDPOINT}"
            
            self.s3_client = boto3.client(
                's3',
                endpoint_url=endpoint,
                aws_access_key_id=settings.MINIO_ACCESS_KEY,
                aws_secret_access_key=settings.MINIO_SECRET_KEY,
                config=Config(signature_version='s3v4'),
                verify=settings.MINIO_SECURE
            )
            # Try list buckets to check health
            self.s3_client.list_buckets()
            logger.info("Successfully established MinIO/S3 connection and verified bucket list API.")
        except Exception as e:
            logger.error(f"S3/MinIO connection failed: {e}")
            raise e

    def check_health(self) -> bool:
        if not self.s3_client:
            return False
        try:
            self.s3_client.list_buckets()
            return True
        except Exception as e:
            logger.error(f"S3/MinIO health check failed: {e}")
            return False

storage_client = StorageManager()
