"""Temporal Graph Snapshots modeling network evolution across time."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from ai.digital_twin.schema import InteractomeSnapshot, NetworkEdgeEvidence

logger = logging.getLogger(__name__)


class TemporalGraphManager:
    """Maintains dynamic interactome snapshots across progressive time intervals."""

    def __init__(self) -> None:
        pass

    def compute_edge_turnover(
        self,
        snapshot_t0: InteractomeSnapshot,
        snapshot_t1: InteractomeSnapshot
    ) -> Dict[str, Any]:
        """Calculates gained, lost, and sustained edges between two temporal snapshots."""
        edges_t0 = {(e.source, e.target) for e in snapshot_t0.edges}
        edges_t1 = {(e.source, e.target) for e in snapshot_t1.edges}

        gained = edges_t1 - edges_t0
        lost = edges_t0 - edges_t1
        sustained = edges_t0.intersection(edges_t1)

        total_union = len(edges_t0.union(edges_t1))
        jaccard_stability = len(sustained) / max(1, total_union)

        return {
            "time_interval": f"{snapshot_t0.version_id} ➔ {snapshot_t1.version_id}",
            "gained_edges_count": len(gained),
            "lost_edges_count": len(lost),
            "sustained_edges_count": len(sustained),
            "jaccard_stability": round(jaccard_stability, 3),
            "gained_sample": [{"source": s, "target": t} for s, t in list(gained)[:5]],
            "lost_sample": [{"source": s, "target": t} for s, t in list(lost)[:5]]
        }
