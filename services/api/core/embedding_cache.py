import json
import hashlib
import numpy as np
from typing import Optional, Dict, Any
from services.api.core.redis import redis_client
from services.api.core.logging import logger

class EmbeddingCache:
    def __init__(self, ttl_seconds: int = 86400):
        self.ttl = ttl_seconds

    def _get_key(self, sequence: str, model_name: str) -> str:
        # Compute SHA256 hash of sequence
        sha = hashlib.sha256(sequence.encode("utf-8")).hexdigest()
        return f"protein_emb:{sha}:{model_name.lower()}"

    async def get_embedding(self, sequence: str, model_name: str) -> Optional[Dict[str, np.ndarray]]:
        """Queries Redis for cached per_residue and pooled embeddings."""
        r = redis_client.client
        if r is None:
            return None
            
        key = self._get_key(sequence, model_name)
        try:
            cached_data = await r.get(key)
            if cached_data:
                logger.info(f"Cache hit for sequence hash: {key}")
                payload = json.loads(cached_data)
                
                # Reconstruct numpy arrays
                return {
                    "per_residue": np.array(payload["per_residue"], dtype=np.float32),
                    "pooled": np.array(payload["pooled"], dtype=np.float32)
                }
        except Exception as e:
            logger.warning(f"Failed to fetch from Redis embedding cache: {e}")
            
        return None

    async def set_embedding(self, sequence: str, model_name: str, embeddings: Dict[str, np.ndarray]):
        """Caches per_residue and pooled embeddings in Redis."""
        r = redis_client.client
        if r is None:
            return
            
        key = self._get_key(sequence, model_name)
        try:
            payload = {
                "per_residue": embeddings["per_residue"].tolist(),
                "pooled": embeddings["pooled"].tolist()
            }
            await r.set(key, json.dumps(payload), ex=self.ttl)
            logger.info(f"Cached sequence embedding in Redis under: {key}")
        except Exception as e:
            logger.warning(f"Failed to write to Redis embedding cache: {e}")

embedding_cache = EmbeddingCache()
