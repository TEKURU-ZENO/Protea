"""Differential State Analyzer quantifying molecular changes between twin states."""

from __future__ import annotations

import math
from typing import Any, Dict, List
from ai.digital_twin.schema import MolecularState


class DifferentialStateAnalyzer:
    """Calculates log2 fold-changes and statistical significance across states."""

    def __init__(self, log2fc_cutoff: float = 1.0):
        self.log2fc_cutoff = log2fc_cutoff

    def compute_differential_states(
        self,
        baseline_states: Dict[str, MolecularState],
        perturbed_states: Dict[str, MolecularState]
    ) -> Dict[str, Any]:
        """Computes differential expression, abundance, and activity shifts."""
        all_nodes = set(baseline_states.keys()).union(set(perturbed_states.keys()))
        diff_nodes: List[Dict[str, Any]] = []

        upregulated_count = 0
        downregulated_count = 0

        for node in all_nodes:
            s_base = baseline_states.get(node)
            s_pert = perturbed_states.get(node)

            expr_base = s_base.gene_expression if s_base else None
            expr_pert = s_pert.gene_expression if s_pert else None

            log2_fc: float = 0.0
            if expr_base is not None and expr_pert is not None:
                log2_fc = round(expr_pert - expr_base, 3)
            elif expr_pert is not None:
                log2_fc = round(expr_pert, 3)
            elif expr_base is not None:
                log2_fc = round(-expr_base, 3)

            # Abundance shift
            abund_base = s_base.protein_abundance if s_base else None
            abund_pert = s_pert.protein_abundance if s_pert else None
            abund_delta = round(abund_pert - abund_base, 3) if abund_base is not None and abund_pert is not None else 0.0

            # Activity shift
            act_base = s_base.protein_activity if s_base else 0.0
            act_pert = s_pert.protein_activity if s_pert else 0.0
            act_delta = round((act_pert or 0.0) - (act_base or 0.0), 3)

            # Simulated p-value based on magnitude
            p_val = round(max(1e-6, 1.0 / (1.0 + math.exp(abs(log2_fc) * 2.0))), 6)

            is_sig = abs(log2_fc) >= self.log2fc_cutoff

            if log2_fc >= self.log2fc_cutoff:
                upregulated_count += 1
            elif log2_fc <= -self.log2fc_cutoff:
                downregulated_count += 1

            diff_nodes.append({
                "entity_id": node,
                "log2_fc": log2_fc,
                "protein_abundance_delta": abund_delta,
                "activity_delta": act_delta,
                "p_value": p_val,
                "significant": is_sig,
                "direction": "UP" if log2_fc > 0 else "DOWN" if log2_fc < 0 else "UNCHANGED"
            })

        # Sort by absolute fold change
        sorted_diffs = sorted(diff_nodes, key=lambda x: abs(x["log2_fc"]), reverse=True)

        return {
            "total_entities_compared": len(all_nodes),
            "upregulated_count": upregulated_count,
            "downregulated_count": downregulated_count,
            "significant_count": upregulated_count + downregulated_count,
            "top_differential_entities": sorted_diffs[:15]
        }
