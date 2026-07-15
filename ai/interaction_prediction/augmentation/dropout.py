import torch
from typing import Tuple

class GraphAugmentor:
    @staticmethod
    def edge_dropout(edge_index: torch.Tensor, p: float = 0.15) -> torch.Tensor:
        """Randomly drops a percentage of edges to prevent GNN over-smoothing."""
        if p <= 0.0 or p >= 1.0:
            return edge_index
            
        num_edges = edge_index.shape[1]
        mask = torch.rand(num_edges) > p
        return edge_index[:, mask]

    @staticmethod
    def feature_mask(x: torch.Tensor, p: float = 0.1) -> torch.Tensor:
        """Randomly masks a percentage of node features."""
        if p <= 0.0 or p >= 1.0:
            return x
            
        mask = torch.rand(x.shape) > p
        return x * mask.to(x.dtype)
