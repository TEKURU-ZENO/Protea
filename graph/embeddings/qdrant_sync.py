from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import Dict, Any, List, Optional
from services.api.core.config import settings
from services.api.core.logging import logger
from services.api.core.vector_db import qdrant_client

class QdrantSyncManager:
    def __init__(self):
        # We reuse the client from services.api.core.vector_db if connected, 
        # or construct a fallback local client.
        self._client = qdrant_client

    @property
    def client(self) -> Optional[QdrantClient]:
        if not self._client.client:
            try:
                self._client.connect()
            except Exception as e:
                logger.error(f"Cannot initialize QdrantClient connection in Sync: {e}")
        return self._client.client

    def init_collections(self):
        """Initializes proteins_esm2, proteins_protbert, and proteins_fused collections if missing."""
        c = self.client
        if not c:
            logger.warning("Qdrant Client not online. Bypassing collection initialization.")
            return

        # Collection definitions: Name -> Vector Dimension
        collections_to_create = {
            "proteins_esm2": 1280,      # ESM-2 150M has 640, 650M has 1280. We use 1280 as default.
            "proteins_protbert": 1024,  # ProtBERT dimension
            "proteins_fused": 1024      # Fused projected dimension
        }

        try:
            existing = [col.name for col in c.get_collections().collections]
            for col_name, dim in collections_to_create.items():
                if col_name not in existing:
                    logger.info(f"Creating Qdrant collection: {col_name} (dim: {dim})")
                    c.create_collection(
                        collection_name=col_name,
                        vectors_config=models.VectorParams(
                            size=dim,
                            distance=models.Distance.COSINE
                        )
                    )
            logger.info("Qdrant collections initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing Qdrant collections: {e}")

    def upsert_protein(self, collection_name: str, uniprot_id: str, vector: List[float], payload: Dict[str, Any]):
        """Inserts/Updates protein vector and metadata in specific Qdrant collection."""
        c = self.client
        if not c:
            logger.warning(f"Qdrant offline. Bypassing upsert for {uniprot_id} into {collection_name}.")
            return

        try:
            # Generate stable int-like ID or use string UUID
            # Qdrant supports string IDs directly (UUIDs or normal strings)
            c.upsert(
                collection_name=collection_name,
                points=[
                    models.PointStruct(
                        id=uniprot_id,
                        vector=vector,
                        payload=payload
                    )
                ]
            )
            logger.info(f"Upserted vector for {uniprot_id} into {collection_name}.")
        except Exception as e:
            logger.error(f"Error upserting vector into Qdrant: {e}")

    def search_nearest(self, collection_name: str, query_vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """Queries Qdrant collection to retrieve K nearest neighbors."""
        c = self.client
        if not c:
            logger.warning(f"Qdrant offline. Returning empty search list.")
            return []

        try:
            results = c.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit
            )
            
            output = []
            for res in results:
                output.append({
                    "id": res.id,
                    "score": float(res.score),
                    "payload": res.payload
                })
            return output
        except Exception as e:
            logger.error(f"Error searching Qdrant collection: {e}")
            return []

qdrant_sync = QdrantSyncManager()
