"""Context-specific edge filtering based on tissue expression and cellular localization."""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Set
from ai.digital_twin.schema import NetworkEdgeEvidence

logger = logging.getLogger(__name__)


class ContextFilter:
    """Filters interactome edges based on tissue-specific gene/protein expression and compartments."""

    def __init__(self, min_expression_log2: float = 1.0):
        self.min_expression_log2 = min_expression_log2

    def filter_by_expression(
        self,
        edges: List[NetworkEdgeEvidence],
        expressed_entities: Set[str]
    ) -> List[NetworkEdgeEvidence]:
        """Retains only edges where both interacting partners are expressed in the given biological context."""
        filtered: List[NetworkEdgeEvidence] = []
        for edge in edges:
            if edge.source in expressed_entities and edge.target in expressed_entities:
                filtered.append(edge)
            else:
                logger.debug(f"Filtered edge {edge.source}-{edge.target}: insufficient context expression.")
        return filtered

    def filter_by_compartment(
        self,
        edges: List[NetworkEdgeEvidence],
        compartment_map: Dict[str, str]
    ) -> List[NetworkEdgeEvidence]:
        """Verifies interacting entities share compatible subcellular locations or translocation capability."""
        compatible_edges: List[NetworkEdgeEvidence] = []
        for edge in edges:
            loc_a = compartment_map.get(edge.source)
            loc_b = compartment_map.get(edge.target)

            # If location unannotated or matching, allow
            if not loc_a or not loc_b:
                compatible_edges.append(edge)
                continue

            # Check overlap or cytosol-boundary transit
            compartments_a = set(loc_a.lower().replace("/", "_").split("_"))
            compartments_b = set(loc_b.lower().replace("/", "_").split("_"))

            if compartments_a.intersection(compartments_b) or "cytosol" in compartments_a or "cytosol" in compartments_b:
                compatible_edges.append(edge)
            else:
                logger.debug(f"Edge {edge.source}-{edge.target} failed compartment check: {loc_a} vs {loc_b}")

        return compatible_edges
