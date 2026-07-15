import torch
from typing import Dict, Any, Type
from services.api.core.logging import logger

class BaseFeatureFusion:
    def fuse(self, sequence_emb: torch.Tensor, graph_emb: torch.Tensor) -> torch.Tensor:
        """Fuses sequence embeddings (PLM) and graph topological embeddings."""
        pass

class ConcatenationFusion(BaseFeatureFusion):
    def fuse(self, sequence_emb: torch.Tensor, graph_emb: torch.Tensor) -> torch.Tensor:
        """Direct concatenation of features."""
        # Align lengths if necessary
        return torch.cat([sequence_emb, graph_emb], dim=-1)

class WeightedFusion(BaseFeatureFusion):
    def fuse(self, sequence_emb: torch.Tensor, graph_emb: torch.Tensor) -> torch.Tensor:
        """Weighted sum of features after a projection layer."""
        # Assume input dimensions match, or apply linear projection
        w1, w2 = 0.7, 0.3
        # Match dimensions by trimming/padding for sum fallback
        dim = min(sequence_emb.shape[-1], graph_emb.shape[-1])
        return w1 * sequence_emb[..., :dim] + w2 * graph_emb[..., :dim]

class FusionRegistry:
    def __init__(self):
        self._strategies: Dict[str, BaseFeatureFusion] = {}
        self.register("concatenation", ConcatenationFusion())
        self.register("weighted", WeightedFusion())

    def register(self, name: str, strategy: BaseFeatureFusion):
        self._strategies[name.lower().strip()] = strategy
        logger.info(f"[IPE FUSION] Registered strategy: {name}")

    def get(self, name: str) -> BaseFeatureFusion:
        name_clean = name.lower().strip()
        if name_clean not in self._strategies:
            return self._strategies["concatenation"]
        return self._strategies[name_clean]

fusion_registry = FusionRegistry()
