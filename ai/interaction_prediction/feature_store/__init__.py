import numpy as np
from typing import Dict, Optional
from services.api.core.logging import logger

class FeatureStore:
    def __init__(self):
        # In-memory dictionary caches
        self._protein_cache: Dict[str, np.ndarray] = {}
        self._graph_cache: Dict[str, np.ndarray] = {}

    def get_protein_features(self, protein_id: str) -> Optional[np.ndarray]:
        """Retrieves cached protein PLM embedding vectors."""
        return self._protein_cache.get(protein_id.strip())

    def set_protein_features(self, protein_id: str, features: np.ndarray):
        """Caches protein PLM embedding vectors."""
        self._protein_cache[protein_id.strip()] = features

    def get_graph_features(self, version: str) -> Optional[np.ndarray]:
        """Retrieves cached GNN node representation maps."""
        return self._graph_cache.get(version.strip())

    def set_graph_features(self, version: str, embeddings: np.ndarray):
        """Caches graph representation snapshot maps."""
        self._graph_cache[version.strip()] = embeddings

feature_store = FeatureStore()
