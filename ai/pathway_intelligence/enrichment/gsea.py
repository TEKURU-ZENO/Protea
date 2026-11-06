"""
PROTEA PaIE - Gene Set Enrichment Analysis (GSEA) & Gene Set Variation Analysis (GSVA)
Ranked enrichment and single-sample pathway variation analytics.
"""

from typing import List, Dict, Tuple, Optional, Any
import numpy as np
import logging
from ai.pathway_intelligence.registry import paie_registry
from ai.pathway_intelligence.enrichment.statistics import benjamini_hochberg

logger = logging.getLogger("ai.pathway_intelligence.enrichment.gsea")

@paie_registry.register_enrichment_engine("gsea")
class GSEAEngine:
    """Ranked Gene Set Enrichment Analysis calculating running sum statistics."""

    def __init__(self, n_permutations: int = 100):
        self.n_permutations = n_permutations

    def run_gsea(
        self,
        ranked_genes: List[Tuple[str, float]],
        pathway_genes: List[str],
        weight: float = 1.0
    ) -> Dict[str, Any]:
        """
        Execute standard GSEA running sum algorithm for a single gene set.
        ranked_genes: list of (gene_symbol, ranking_metric) sorted descending.
        """
        gene_names = [g[0].upper() for g in ranked_genes]
        metrics = np.array([abs(g[1]) ** weight for g in ranked_genes], dtype=float)
        N = len(gene_names)
        gene_set = set(p.upper() for p in pathway_genes)

        in_set = np.array([g in gene_set for g in gene_names], dtype=bool)
        n_hits = np.sum(in_set)
        n_miss = N - n_hits

        if n_hits == 0 or n_miss == 0:
            return {"es": 0.0, "nes": 0.0, "p_value": 1.0, "lead_genes": []}

        # Step weights
        hit_sum = np.sum(metrics[in_set])
        if hit_sum == 0:
            return {"es": 0.0, "nes": 0.0, "p_value": 1.0, "lead_genes": []}

        # Vectorized running sum calculation
        step_hit = np.where(in_set, metrics / hit_sum, 0.0)
        step_miss = np.where(~in_set, -1.0 / n_miss, 0.0)
        running_sum = np.cumsum(step_hit + step_miss)

        max_val = float(np.max(running_sum))
        min_val = float(np.min(running_sum))
        es = max_val if abs(max_val) > abs(min_val) else min_val

        # Find leading edge genes (up to peak of running sum)
        peak_idx = int(np.argmax(running_sum) if es >= 0 else np.argmin(running_sum))
        lead_genes = [gene_names[i] for i in range(peak_idx + 1) if in_set[i]]

        # Permutation testing for empirical p-value
        perm_scores = []
        for _ in range(self.n_permutations):
            perm_in_set = np.random.permutation(in_set)
            perm_hit_sum = np.sum(metrics[perm_in_set])
            if perm_hit_sum == 0:
                continue
            perm_step_hit = np.where(perm_in_set, metrics / perm_hit_sum, 0.0)
            perm_step_miss = np.where(~perm_in_set, -1.0 / n_miss, 0.0)
            perm_running = np.cumsum(perm_step_hit + perm_step_miss)
            p_max = float(np.max(perm_running))
            p_min = float(np.min(perm_running))
            p_es = p_max if abs(p_max) > abs(p_min) else p_min
            perm_scores.append(p_es)

        perm_arr = np.array(perm_scores)
        if es >= 0:
            pos_perms = perm_arr[perm_arr >= 0]
            p_val = float(np.sum(pos_perms >= es) / len(pos_perms)) if len(pos_perms) > 0 else 0.05
            mean_pos = float(np.mean(pos_perms)) if len(pos_perms) > 0 else 1.0
            nes = es / mean_pos if mean_pos != 0 else es
        else:
            neg_perms = perm_arr[perm_arr < 0]
            p_val = float(np.sum(neg_perms <= es) / len(neg_perms)) if len(neg_perms) > 0 else 0.05
            mean_neg = float(abs(np.mean(neg_perms))) if len(neg_perms) > 0 else 1.0
            nes = es / mean_neg if mean_neg != 0 else es

        return {
            "es": float(es),
            "nes": float(nes),
            "p_value": max(0.001, min(1.0, p_val)),
            "leading_edge_size": len(lead_genes),
            "leading_edge_genes": lead_genes[:10]
        }


@paie_registry.register_enrichment_engine("gsva")
class GSVAEngine:
    """Gene Set Variation Analysis for unsupervised single-sample pathway activity estimation."""

    def calculate_activity(self, sample_expression: Dict[str, float], pathway_genes: List[str]) -> float:
        """Calculate single-sample Kolmogorov-Smirnov pathway variation score."""
        sorted_genes = sorted(sample_expression.items(), key=lambda x: x[1], reverse=True)
        gene_names = [g[0].upper() for g in sorted_genes]
        pw_set = set(p.upper() for p in pathway_genes)

        in_set = np.array([g in pw_set for g in gene_names], dtype=bool)
        n_hits = np.sum(in_set)
        n_miss = len(gene_names) - n_hits

        if n_hits == 0 or n_miss == 0:
            return 0.0

        step_hit = np.where(in_set, 1.0 / n_hits, 0.0)
        step_miss = np.where(~in_set, -1.0 / n_miss, 0.0)
        running = np.cumsum(step_hit + step_miss)

        max_dev = float(np.max(running))
        min_dev = float(np.min(running))
        return max_dev + min_dev # Standard GSVA difference formulation
