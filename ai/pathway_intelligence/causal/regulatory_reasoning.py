"""
PROTEA PaIE - Regulatory Reasoning & Causal Sign Propagation
Distinguishes directed activation vs inhibition and computes net causal impacts along signaling cascades.
"""

from typing import List, Dict, Tuple, Optional, Any
import networkx as nx
import logging
from ai.pathway_intelligence.registry import paie_registry

logger = logging.getLogger("ai.pathway_intelligence.causal.regulatory")

SIGN_MAP = {
    "activates": 1,
    "phosphorylates": 1,
    "upregulates": 1,
    "cleaves": 1,
    "inhibits": -1,
    "dephosphorylates": -1,
    "downregulates": -1,
    "ubiquitinates": -1,
    "complex_formation": 1,
    "unknown": 0
}

@paie_registry.register_causal_engine("regulatory_reasoning")
class RegulatoryReasoningEngine:
    """Evaluates regulatory directions, signed cascade effects, and causal consistency."""

    def evaluate_cascade_causality(self, path: List[str], directed_graph: nx.DiGraph) -> Dict[str, Any]:
        """
        Evaluate net causal sign and mechanisms along a sequence of interacting nodes:
        [P1, P2, ..., Pn].
        Net sign = Product of individual edge signs (+1: net activation, -1: net inhibition, 0: ambiguous).
        """
        if len(path) < 2:
            return {"path": path, "net_effect": "neutral", "sign": 0, "steps": []}

        steps = []
        net_sign = 1

        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            if directed_graph.has_edge(u, v):
                edge_data = directed_graph[u][v]
                rel_type = edge_data.get("type", edge_data.get("interaction_type", "activates"))
                confidence = edge_data.get("weight", edge_data.get("confidence", 0.85))
            else:
                rel_type = "unknown"
                confidence = 0.50

            sign = SIGN_MAP.get(rel_type.lower(), 0)
            net_sign *= sign if sign != 0 else 1

            steps.append({
                "source": u,
                "target": v,
                "mechanism": rel_type,
                "sign": sign,
                "confidence": confidence
            })

        effect_label = "Activation" if net_sign > 0 else ("Inhibition" if net_sign < 0 else "Ambiguous")

        return {
            "path": path,
            "length": len(path) - 1,
            "net_sign": net_sign,
            "net_effect": effect_label,
            "steps": steps,
            "cumulative_confidence": round(float(min(s["confidence"] for s in steps)), 3)
        }

    def infer_perturbation_impact(
        self,
        perturbed_protein: str,
        perturbation_type: str, # "knockout", "overexpression", "inhibition"
        graph: nx.DiGraph,
        max_depth: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Simulate downstream functional consequences of perturbing a specific node.
        """
        prot = perturbed_protein.upper()
        if prot not in graph:
            return []

        initial_delta = -1 if perturbation_type in ["knockout", "inhibition"] else 1
        impacts = []

        # Breadth-first traversal up to max_depth
        visited = {prot: initial_delta}
        queue = [(prot, initial_delta, 0)]

        while queue:
            curr, curr_sign, depth = queue.pop(0)
            if depth >= max_depth:
                continue

            for target in graph.successors(curr):
                edge_type = graph[curr][target].get("type", "activates")
                edge_sign = SIGN_MAP.get(edge_type.lower(), 1)
                predicted_target_delta = curr_sign * edge_sign

                if target not in visited:
                    visited[target] = predicted_target_delta
                    queue.append((target, predicted_target_delta, depth + 1))
                    impacts.append({
                        "protein": target,
                        "upstream_source": curr,
                        "regulatory_mechanism": edge_type,
                        "predicted_state": "Downregulated / Suppressed" if predicted_target_delta < 0 else "Upregulated / Activated",
                        "sign": predicted_target_delta,
                        "cascade_depth": depth + 1
                    })

        return impacts
