import json
from typing import Optional, List, Dict, Any
from services.api.core.redis import redis_client
from services.api.core.logging import logger

class GraphCache:
    def __init__(self, ttl_seconds: int = 3600):
        self.ttl = ttl_seconds

    async def get_path(self, p1: str, p2: str) -> Optional[List[Dict[str, Any]]]:
        r = redis_client.client
        if not r:
            return None
        key = f"graph_path:{p1}:{p2}"
        try:
            val = await r.get(key)
            if val:
                logger.info(f"Graph Cache hit for path: {key}")
                return json.loads(val)
        except Exception as e:
            logger.warning(f"Error querying Redis graph path cache: {e}")
        return None

    async def set_path(self, p1: str, p2: str, path: List[Dict[str, Any]]):
        r = redis_client.client
        if not r:
            return
        key = f"graph_path:{p1}:{p2}"
        try:
            await r.set(key, json.dumps(path), ex=self.ttl)
        except Exception as e:
            logger.warning(f"Error setting Redis graph path cache: {e}")

    async def get_neighbors(self, protein_id: str) -> Optional[List[Dict[str, Any]]]:
        r = redis_client.client
        if not r:
            return None
        key = f"graph_neighbors:{protein_id}"
        try:
            val = await r.get(key)
            if val:
                logger.info(f"Graph Cache hit for neighbors: {key}")
                return json.loads(val)
        except Exception as e:
            logger.warning(f"Error querying Redis graph neighbors cache: {e}")
        return None

    async def set_neighbors(self, protein_id: str, neighbors: List[Dict[str, Any]]):
        r = redis_client.client
        if not r:
            return
        key = f"graph_neighbors:{protein_id}"
        try:
            await r.set(key, json.dumps(neighbors), ex=self.ttl)
        except Exception as e:
            logger.warning(f"Error setting Redis graph neighbors cache: {e}")

graph_cache = GraphCache()
