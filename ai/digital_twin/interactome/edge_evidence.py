"""Edge evidence provenance tracker and scoring."""

from __future__ import annotations

from typing import Any, Dict, List
from ai.digital_twin.schema import NetworkEdgeEvidence


class EdgeEvidenceTracker:
    """Manages evidence provenance and confidence calibration for interactome edges."""

    def compute_edge_weight(self, edge: NetworkEdgeEvidence) -> float:
        """Computes calibrated edge weight incorporating status and source count."""
        base_confidence = edge.confidence
        
        status_multipliers = {
            "OBSERVED": 1.0,
            "CURATED": 0.90,
            "INFERRED": 0.75,
            "PREDICTED": 0.60
        }
        multiplier = status_multipliers.get(edge.edge_status, 0.70)
        
        # Source redundancy bonus
        source_count = len(edge.evidence_sources)
        bonus = min(0.15, (source_count - 1) * 0.05) if source_count > 1 else 0.0

        return round(min(1.0, (base_confidence * multiplier) + bonus), 4)

    def summarize_provenance(self, edges: List[NetworkEdgeEvidence]) -> Dict[str, Any]:
        """Provides statistical breakdown of edge provenance in the interactome."""
        status_counts = {"OBSERVED": 0, "CURATED": 0, "INFERRED": 0, "PREDICTED": 0}
        type_counts: Dict[str, int] = {}
        directed_count = 0

        for e in edges:
            status_counts[e.edge_status] = status_counts.get(e.edge_status, 0) + 1
            type_counts[e.edge_type] = type_counts.get(e.edge_type, 0) + 1
            if e.directed:
                directed_count += 1

        return {
            "total_edges": len(edges),
            "status_distribution": status_counts,
            "type_distribution": type_counts,
            "directed_ratio": round(directed_count / max(1, len(edges)), 3)
        }
