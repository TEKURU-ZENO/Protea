"""Missingness-Aware State Estimator imputing unmeasured molecular features."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from ai.digital_twin.schema import MolecularState, NetworkEdgeEvidence, StateStatus

logger = logging.getLogger(__name__)


class StateEstimator:
    """Estimates unobserved biological state variables via interactome topology and multi-omics correlation."""

    def __init__(self, k_neighbors: int = 3, mrna_protein_correlation: float = 0.65):
        self.k_neighbors = k_neighbors
        self.mrna_protein_correlation = mrna_protein_correlation

    def estimate_missing_states(
        self,
        states: Dict[str, MolecularState],
        edges: List[NetworkEdgeEvidence]
    ) -> Dict[str, MolecularState]:
        """Imputes missing attributes across nodes using neighbor propagation and cross-modality scaling."""
        updated_states = {k: MolecularState(**v.to_dict()) for k, v in states.items()}

        # Build neighbor index
        neighbors: Dict[str, List[str]] = {n: [] for n in updated_states}
        for e in edges:
            if e.source in neighbors and e.target in neighbors:
                neighbors[e.source].append(e.target)
                neighbors[e.target].append(e.source)

        for entity_id, state in updated_states.items():
            # 1. Estimate protein abundance if expression is present but abundance is missing
            if state.protein_abundance is None and state.gene_expression is not None:
                # Biological empirical scaling: protein = expression * correlation + basal_offset
                estimated_abundance = round(state.gene_expression * self.mrna_protein_correlation + 1.2, 2)
                state.protein_abundance = estimated_abundance
                state.imputed_fields.append("protein_abundance")
                state.status = StateStatus.ESTIMATED.value
                state.confidence = round(state.confidence * 0.85, 3)

            # 2. Estimate activity from active upstream regulators or topological neighbors
            if state.protein_activity is None:
                adj = neighbors.get(entity_id, [])
                observed_neighbor_acts = [
                    updated_states[nbr].protein_activity
                    for nbr in adj
                    if updated_states[nbr].protein_activity is not None
                ]
                if observed_neighbor_acts:
                    mean_activity = sum(observed_neighbor_acts) / len(observed_neighbor_acts)
                    state.protein_activity = round(mean_activity * 0.80, 2)
                    state.imputed_fields.append("protein_activity")
                    state.status = StateStatus.ESTIMATED.value
                    state.confidence = round(state.confidence * 0.75, 3)
                else:
                    state.protein_activity = 0.0  # Neutral baseline
                    state.imputed_fields.append("protein_activity")
                    state.status = StateStatus.ESTIMATED.value
                    state.confidence = round(state.confidence * 0.60, 3)

            # 3. Estimate pathway activity if missing
            if state.pathway_activity is None:
                state.pathway_activity = round(
                    ((state.gene_expression or 5.0) - 5.0) / 3.0 + (state.protein_activity or 0.0) * 0.5,
                    2
                )
                state.imputed_fields.append("pathway_activity")

        return updated_states
