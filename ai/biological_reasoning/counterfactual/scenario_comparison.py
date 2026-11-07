"""
PROTEA BRE - Counterfactual & Perturbation Reasoning Engine
Simulates in silico gene knockouts, overexpression, and pharmacological inhibition on downstream networks.
"""

from typing import List, Dict, Optional, Any
import networkx as nx
from ai.biological_reasoning.schema import PerturbationScenario
from ai.biological_reasoning.mechanistic.mechanism_reconstructor import SIGN_MAP
from ai.pathway_intelligence.ingestion.reactome import ReactomeAdapter

class CounterfactualReasoningEngine:
    """Simulates biological perturbations and calculates network-wide downstream changes."""

    def __init__(self):
        self.reactome = ReactomeAdapter()
        self._regulatory_network = self._init_regulatory_network()

    def _init_regulatory_network(self) -> nx.DiGraph:
        dg = nx.DiGraph()
        edges = [
            ("USP7", "MDM2", "stabilization", 0.88),
            ("MDM2", "TP53", "ubiquitination", 0.96),
            ("ATM", "CHEK2", "phosphorylates", 0.98),
            ("CHEK2", "TP53", "phosphorylates", 0.94),
            ("TP53", "BAX", "transcriptional_activation", 0.92),
            ("TP53", "CDKN1A", "transcriptional_activation", 0.95),
            ("BCL2", "BAX", "inhibits", 0.95),
            ("BAX", "CASP3", "cleaves", 0.90),
            ("PTEN", "AKT1", "phosphatase_inhibition", 0.93),
            ("AKT1", "MTOR", "activates", 0.96),
            ("AKT1", "BAD", "inhibits", 0.91),
            ("BAD", "BCL2", "inhibits", 0.89),
            ("CDKN1A", "CDK2", "inhibits", 0.92),
            ("CDK2", "RB1", "phosphorylates", 0.93),
            ("RB1", "E2F1", "inhibits", 0.97)
        ]
        for u, v, rel, w in edges:
            dg.add_edge(u, v, mechanism=rel, weight=w)
        return dg

    def simulate_perturbation(
        self,
        target_protein: str,
        perturbation_type: str = "knockout", # knockout, knockdown, overexpression, inhibition
        tissue: Optional[str] = None,
        max_depth: int = 3
    ) -> PerturbationScenario:
        """
        Simulate perturbation impact:
        Knockout/Inhibition = -1.0 initial delta
        Overexpression/Activation = +1.0 initial delta
        Propagates deltas through signed network: delta_v = delta_u * sign(u -> v) * weight
        """
        target = target_protein.upper()
        initial_delta = -1.0 if perturbation_type in ["knockout", "knockdown", "inhibition"] else 1.0

        perturbed_nodes = {target: initial_delta}
        affected_pathways = []

        if target in self._regulatory_network:
            visited = {target: initial_delta}
            queue = [(target, initial_delta, 0)]

            while queue:
                curr, curr_delta, depth = queue.pop(0)
                if depth >= max_depth:
                    continue

                for successor in self._regulatory_network.successors(curr):
                    e_data = self._regulatory_network[curr][successor]
                    mech = e_data.get("mechanism", "activates")
                    sign = SIGN_MAP.get(mech.lower(), 1)
                    weight = e_data.get("weight", 0.85)

                    pred_delta = curr_delta * sign * weight

                    if successor not in visited:
                        visited[successor] = pred_delta
                        perturbed_nodes[successor] = round(pred_delta, 3)
                        queue.append((successor, pred_delta, depth + 1))

        # Identify impacted pathways
        for node in list(perturbed_nodes.keys())[:5]:
            pws = self.reactome.get_pathways_for_protein(node)
            for pw in pws:
                if not any(ap["pathway_id"] == pw["id"] for ap in affected_pathways):
                    affected_pathways.append({
                        "pathway_id": pw["id"],
                        "name": pw["name"],
                        "driver_protein": node,
                        "predicted_state": "Suppressed" if perturbed_nodes[node] < 0 else "Hyper-activated"
                    })

        qualifications = [
            "Simulation is a computational graph-propagation prediction, not an in vitro or in vivo validated causal fact.",
            "Assumes linear signal propagation and ignores non-linear transcriptional saturation thresholds.",
            "Tissue-specific feedback loops or alternative splicing variants may alter cellular responsiveness."
        ]

        return PerturbationScenario(
            target_protein=target,
            perturbation_type=perturbation_type,
            tissue=tissue,
            propagation_depth=max_depth,
            perturbed_nodes=perturbed_nodes,
            affected_pathways=affected_pathways[:6],
            model_qualifications=qualifications
        )
