"""
PROTEA PaIE - Pathway Representation Learning & Embeddings
Aggregates constituent protein embeddings into fixed-dimensional pathway representations.
"""

from typing import List, Dict, Optional, Any
import numpy as np

class PathwayEmbeddingAggregator:
    """Aggregates protein representations into unified pathway-level vectors."""

    def __init__(self, embedding_dim: int = 1280):
        self.embedding_dim = embedding_dim

    def aggregate_pathway(
        self,
        protein_embeddings: Dict[str, np.ndarray],
        method: str = "mean"
    ) -> np.ndarray:
        """
        Aggregate protein vectors into a single pathway embedding.
        Methods: 'mean', 'max', 'l2_normalized'
        """
        if not protein_embeddings:
            return np.zeros(self.embedding_dim, dtype=np.float32)

        vectors = list(protein_embeddings.values())
        mat = np.vstack(vectors)

        if method == "mean":
            agg = np.mean(mat, axis=0)
        elif method == "max":
            agg = np.max(mat, axis=0)
        else:
            agg = np.mean(mat, axis=0)

        norm = np.linalg.norm(agg)
        if norm > 0:
            agg = agg / norm
        return agg.astype(np.float32)

    def calculate_pathway_similarity(self, emb_a: np.ndarray, emb_b: np.ndarray) -> float:
        """Cosine similarity between two pathway vectors."""
        norm_a = np.linalg.norm(emb_a)
        norm_b = np.linalg.norm(emb_b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(emb_a, emb_b) / (norm_a * norm_b))
