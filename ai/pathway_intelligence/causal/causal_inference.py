"""
PROTEA PaIE - Causal Inference & Reverse Causal Reasoning (RCR)
Infers causal upstream master regulators from downstream gene expression or interaction perturbations.
"""

from typing import List, Dict, Set, Optional, Any
import networkx as nx
import numpy as np

class ReverseCausalReasoning:
    """Infers upstream master regulators explaining observed downstream changes."""

    def infer_upstream_regulators(
        self,
        differentially_expressed_nodes: Dict[str, int], # {"GENE": +1 (up) or -1 (down)}
        causal_graph: nx.DiGraph,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Evaluate candidate master regulators based on concordance with observed gene states.
        Concordance = (Correctly predicted downstream signs) / (Total regulated downstream nodes).
        """
        candidates = []

        for candidate in causal_graph.nodes():
            downstream = list(causal_graph.successors(candidate))
            if not downstream:
                continue

            matches = 0
            tested = 0

            for target in downstream:
                if target in differentially_expressed_nodes:
                    tested += 1
                    observed_sign = differentially_expressed_nodes[target]
                    edge_type = causal_graph[candidate][target].get("type", "activates")
                    predicted_sign = 1 if edge_type in ["activates", "phosphorylates", "upregulates"] else -1

                    if observed_sign == predicted_sign:
                        matches += 1

            if tested > 0:
                concordance = matches / tested
                candidates.append({
                    "regulator": candidate,
                    "concordance": round(concordance, 3),
                    "tested_targets": tested,
                    "concordant_targets": matches,
                    "downstream_degree": len(downstream)
                })

        candidates.sort(key=lambda c: (-c["concordance"], -c["tested_targets"]))
        return candidates[:top_k]
