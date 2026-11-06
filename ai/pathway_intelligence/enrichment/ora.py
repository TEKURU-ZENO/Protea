"""
PROTEA PaIE - Over-Representation Analysis (ORA) Engine
Performs statistical enrichment testing using Hypergeometric distribution / Fisher's exact test.
"""

from typing import List, Dict, Set, Optional, Any
import numpy as np
from scipy import stats
import logging
from ai.pathway_intelligence.registry import paie_registry
from ai.pathway_intelligence.enrichment.statistics import benjamini_hochberg
from ai.pathway_intelligence.ingestion.reactome import ReactomeAdapter

logger = logging.getLogger("ai.pathway_intelligence.enrichment.ora")

@paie_registry.register_enrichment_engine("ora")
class ORAEngine:
    """Over-Representation Analysis engine testing gene list enrichment against pathway libraries."""

    def __init__(self, background_size: int = 20000):
        self.background_size = background_size
        self.reactome = ReactomeAdapter()

    def run_enrichment(
        self,
        gene_list: List[str],
        p_cutoff: float = 0.05,
        min_overlap: int = 2,
        custom_pathways: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute ORA against reference pathways using hypergeometric survival function.
        """
        input_genes = set(g.strip().upper() for g in gene_list if g.strip())
        n = len(input_genes)
        if n == 0:
            return []

        pathways = custom_pathways or self.reactome.list_all_pathways()
        N = self.background_size

        raw_results = []
        p_values = []

        for pw in pathways:
            pw_id = pw["id"]
            pw_name = pw["name"]
            pw_genes = set(p.upper() for p in pw["proteins"])
            K = len(pw_genes)

            overlap = input_genes & pw_genes
            k = len(overlap)

            if k < min_overlap:
                continue

            # Hypergeometric test: P(X >= k)
            # scipy.stats.hypergeom.sf(k - 1, M, n, N) where:
            # M = population size (N), n = successes in pop (K), N = sample size (n)
            p_val = float(stats.hypergeom.sf(k - 1, N, K, n))

            raw_results.append({
                "pathway_id": pw_id,
                "name": pw_name,
                "category": pw.get("category", "Biological Process"),
                "p_value": p_val,
                "overlap_count": k,
                "pathway_size": K,
                "input_size": n,
                "overlap_genes": sorted(list(overlap)),
                "fold_enrichment": (k / n) / (K / N) if K > 0 and n > 0 else 0.0
            })
            p_values.append(p_val)

        if not raw_results:
            return []

        # Apply Benjamini-Hochberg FDR correction
        q_values = benjamini_hochberg(p_values)
        for i, q in enumerate(q_values):
            raw_results[i]["q_value"] = float(q)

        # Filter by p_value cutoff and sort by significance
        significant = [r for r in raw_results if r["p_value"] <= p_cutoff]
        significant.sort(key=lambda x: (x["p_value"], -x["fold_enrichment"]))
        return significant
