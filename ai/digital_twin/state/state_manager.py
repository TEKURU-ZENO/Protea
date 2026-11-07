"""Digital Twin State Manager coordinator."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from ai.digital_twin.schema import MolecularState, StateStatus
from ai.digital_twin.state.molecular_state import MolecularStateManager
from ai.digital_twin.state.state_estimator import StateEstimator
from ai.digital_twin.state.state_schema import STATE_DIMENSIONS

logger = logging.getLogger(__name__)


class BiologicalStateManager:
    """Manages state querying, validation, and estimation for digital twin instances."""

    def __init__(self) -> None:
        self.estimator = StateEstimator()

    def get_state_summary(self, states: Dict[str, MolecularState]) -> Dict[str, Any]:
        """Provides statistical summary of completeness and status distribution across the twin."""
        total = len(states)
        if total == 0:
            return {"total_entities": 0, "status_breakdown": {}}

        status_counts = {"OBSERVED": 0, "ESTIMATED": 0, "PREDICTED": 0, "SIMULATED": 0}
        coverage = {
            "gene_expression": 0,
            "protein_abundance": 0,
            "protein_activity": 0,
            "phosphorylation": 0,
            "subcellular_location": 0
        }

        for s in states.values():
            status_counts[s.status] = status_counts.get(s.status, 0) + 1
            if s.gene_expression is not None:
                coverage["gene_expression"] += 1
            if s.protein_abundance is not None:
                coverage["protein_abundance"] += 1
            if s.protein_activity is not None:
                coverage["protein_activity"] += 1
            if s.phosphorylation is not None:
                coverage["phosphorylation"] += 1
            if s.subcellular_location is not None:
                coverage["subcellular_location"] += 1

        return {
            "total_entities": total,
            "status_distribution": status_counts,
            "dimension_coverage": {k: round(v / total, 3) for k, v in coverage.items()},
            "dimensions_metadata": {k: v.__dict__ for k, v in STATE_DIMENSIONS.items()}
        }
