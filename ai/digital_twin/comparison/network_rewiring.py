"""Network Rewiring Analyzer evaluating topological alterations between biological states."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Set
from ai.digital_twin.schema import InteractomeSnapshot, NetworkEdgeEvidence

logger = logging.getLogger(__name__)


class NetworkRewiringAnalyzer:
    """Detects edges gained, lost, or functionally rewired across disease or treatment contexts."""

    def analyze_rewiring(
        self,
        snapshot_baseline: InteractomeSnapshot,
        snapshot_perturbed: InteractomeSnapshot
    ) -> Dict[str, Any]:
        """Compares edge topologies between baseline and perturbed interactomes."""
        base_edges = {(e.source, e.target): e for e in snapshot_baseline.edges}
        pert_edges = {(e.source, e.target): e for e in snapshot_perturbed.edges}

        base_keys = set(base_edges.keys())
        pert_keys = set(pert_edges.keys())

        gained_keys = pert_keys - base_keys
        lost_keys = base_keys - pert_keys
        common_keys = base_keys.intersection(pert_keys)

        rewired_signs: List[Dict[str, Any]] = []
        for k in common_keys:
            e_base = base_edges[k]
            e_pert = pert_edges[k]
            if e_base.sign is not None and e_pert.sign is not None and e_base.sign != e_pert.sign:
                rewired_signs.append({
                    "edge": f"{k[0]} ➔ {k[1]}",
                    "baseline_sign": e_base.sign,
                    "perturbed_sign": e_pert.sign,
                    "mechanism": e_pert.mechanism
                })

        return {
            "gained_edges": [{"source": s, "target": t, "type": pert_edges[(s, t)].edge_type} for s, t in gained_keys],
            "lost_edges": [{"source": s, "target": t, "type": base_edges[(s, t)].edge_type} for s, t in lost_keys],
            "sign_inverted_edges": rewired_signs,
            "turnover_metric": round((len(gained_keys) + len(lost_keys)) / max(1, len(base_keys)), 3)
        }
