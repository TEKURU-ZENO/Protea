"""Molecular State entity handling state persistence and feature vectors."""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional
from ai.digital_twin.schema import MolecularState, StateStatus


class MolecularStateManager:
    """Handles structured operations on node-level molecular states."""

    @staticmethod
    def to_feature_vector(state: MolecularState) -> List[float]:
        """Converts molecular state into fixed numerical feature representation."""
        return [
            state.gene_expression if state.gene_expression is not None else 0.0,
            state.protein_abundance if state.protein_abundance is not None else 0.0,
            state.protein_activity if state.protein_activity is not None else 0.0,
            state.phosphorylation if state.phosphorylation is not None else 0.0,
            state.pathway_activity if state.pathway_activity is not None else 0.0,
            1.0 if state.interaction_status == "active" else 0.0,
            state.confidence
        ]

    @staticmethod
    def compute_euclidean_distance(s1: MolecularState, s2: MolecularState) -> float:
        """Computes distance between two molecular states across observed dimensions."""
        v1 = MolecularStateManager.to_feature_vector(s1)
        v2 = MolecularStateManager.to_feature_vector(s2)
        dist_sq = sum((a - b) ** 2 for a, b in zip(v1[:5], v2[:5]))
        return math.sqrt(dist_sq)
