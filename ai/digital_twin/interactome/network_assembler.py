"""Interactome Network Assembler constructing network graph and computing topology."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Set
from ai.digital_twin.schema import NetworkEdgeEvidence

logger = logging.getLogger(__name__)


class NetworkAssembler:
    """Assembles interactome subgraphs and computes structural graph topology metrics."""

    def assemble_network(
        self,
        nodes: List[str],
        edges: List[NetworkEdgeEvidence]
    ) -> Dict[str, Any]:
        """Validates edges against node set and computes network topology."""
        valid_nodes: Set[str] = set(nodes)
        valid_edges: List[NetworkEdgeEvidence] = [
            e for e in edges if e.source in valid_nodes and e.target in valid_nodes
        ]

        # Build adjacency
        adj: Dict[str, List[Dict[str, Any]]] = {n: [] for n in valid_nodes}
        degrees: Dict[str, int] = {n: 0 for n in valid_nodes}

        for e in valid_edges:
            adj[e.source].append({"target": e.target, "type": e.edge_type, "directed": e.directed, "sign": e.sign, "weight": e.confidence})
            degrees[e.source] = degrees.get(e.source, 0) + 1
            if not e.directed:
                adj[e.target].append({"target": e.source, "type": e.edge_type, "directed": False, "sign": e.sign, "weight": e.confidence})
                degrees[e.target] = degrees.get(e.target, 0) + 1

        n_nodes = len(valid_nodes)
        n_edges = len(valid_edges)
        max_possible_edges = (n_nodes * (n_nodes - 1)) / 2 if n_nodes > 1 else 1
        density = round(n_edges / max_possible_edges, 4)
        avg_degree = round(sum(degrees.values()) / max(1, n_nodes), 2)

        # High-degree hubs
        sorted_hubs = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "node_count": n_nodes,
            "edge_count": n_edges,
            "density": density,
            "average_degree": avg_degree,
            "top_hubs": [{"node": h[0], "degree": h[1]} for h in sorted_hubs],
            "adjacency": adj
        }
