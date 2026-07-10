import numpy as np
from typing import Dict, Any, Optional

class BaseFusionStrategy:
    def fuse(self, sequence_emb: np.ndarray, structure_features: Dict[str, Any]) -> np.ndarray:
        """Combines sequence embedding matrix [seq_len, seq_dim] and structure features 
        to output a canonical projected embedding [seq_len, 1024].
        """
        raise NotImplementedError()

class FusionRegistry:
    def __init__(self):
        self._strategies: Dict[str, BaseFusionStrategy] = {}

    def get(self, name: str) -> BaseFusionStrategy:
        name = name.lower()
        if name not in self._strategies:
            # Fallback to first registered or default
            if "cross_attention" in self._strategies:
                return self._strategies["cross_attention"]
            raise KeyError(f"Fusion strategy '{name}' is not registered.")
        return self._strategies[name]

    def register(self, name: str, strategy: BaseFusionStrategy):
        self._strategies[name.lower()] = strategy

fusion_registry = FusionRegistry()
