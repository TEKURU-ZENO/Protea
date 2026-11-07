"""Context-Aware Interactome Builder coordinator."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Set

from ai.digital_twin.interactome.context_filter import ContextFilter
from ai.digital_twin.interactome.edge_evidence import EdgeEvidenceTracker
from ai.digital_twin.interactome.network_assembler import NetworkAssembler
from ai.digital_twin.schema import BiologicalContext, InteractomeSnapshot, NetworkEdgeEvidence

logger = logging.getLogger(__name__)


class ContextAwareInteractomeBuilder:
    """Assembles high-fidelity context-filtered interactome snapshots."""

    def __init__(self) -> None:
        self.context_filter = ContextFilter()
        self.evidence_tracker = EdgeEvidenceTracker()
        self.network_assembler = NetworkAssembler()

    def build_context_interactome(
        self,
        twin_id: str,
        version_id: str,
        nodes: List[str],
        candidate_edges: List[NetworkEdgeEvidence],
        context: BiologicalContext,
        expressed_nodes: Optional[Set[str]] = None,
        compartment_map: Optional[Dict[str, str]] = None
    ) -> InteractomeSnapshot:
        """Constructs an InteractomeSnapshot honoring context, expression, and compartments."""
        # 1. Filter by expression if provided
        filtered_edges = candidate_edges
        if expressed_nodes:
            filtered_edges = self.context_filter.filter_by_expression(filtered_edges, expressed_nodes)

        # 2. Filter by subcellular compartment
        if compartment_map:
            filtered_edges = self.context_filter.filter_by_compartment(filtered_edges, compartment_map)

        # 3. Re-score confidence using evidence tracker
        for edge in filtered_edges:
            edge.confidence = self.evidence_tracker.compute_edge_weight(edge)

        # 4. Assemble topology
        topology = self.network_assembler.assemble_network(nodes, filtered_edges)
        logger.info(
            f"Built context interactome for {context.tissue_id} ({context.cell_type_id}): "
            f"{topology['node_count']} nodes, {topology['edge_count']} edges, density {topology['density']}."
        )

        snapshot = InteractomeSnapshot(
            snapshot_id=f"SNAP-{twin_id}-{version_id}",
            twin_id=twin_id,
            version_id=version_id,
            nodes=nodes,
            edges=filtered_edges
        )
        snapshot.compute_hash()
        return snapshot
