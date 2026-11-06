"""
PROTEA PaIE - Pathway Prediction & Pathway Completion Engine
Predicts pathway memberships for unannotated proteins and reconstructs missing pathway links.
"""

from typing import List, Dict, Set, Optional, Any
import numpy as np
import networkx as nx
import logging
from ai.pathway_intelligence.registry import paie_registry
from ai.pathway_intelligence.ingestion.reactome import ReactomeAdapter

logger = logging.getLogger("ai.pathway_intelligence.prediction.membership")

@paie_registry.register_prediction_model("pathway_membership")
class PathwayMembershipPredictor:
    """Predicts pathway membership probabilities for proteins using topological context."""

    def __init__(self, reactome_adapter: Optional[ReactomeAdapter] = None):
        self.reactome = reactome_adapter or ReactomeAdapter()

    def predict_membership(
        self,
        protein_id: str,
        pathway_id: str,
        graph: Optional[nx.Graph] = None
    ) -> Dict[str, Any]:
        """
        Evaluate likelihood that protein belongs to pathway_id.
        Integrates:
        1. Known database annotations (if already documented).
        2. Graph topological overlap (Jaccard neighborhood with pathway members).
        3. Average interaction confidence with pathway members.
        """
        prot = protein_id.upper()
        pw = self.reactome.get_pathway(pathway_id)
        if not pw:
            return {"protein_id": prot, "pathway_id": pathway_id, "probability": 0.0, "status": "unknown_pathway"}

        pw_members = set(pw["proteins"])

        # Direct known membership
        if prot in pw_members:
            return {
                "protein_id": prot,
                "pathway_id": pathway_id,
                "pathway_name": pw["name"],
                "probability": 1.0,
                "status": "curated_member",
                "direct_connections": len(pw_members) - 1,
                "confidence_score": 0.99
            }

        # Inference from graph interactions
        if graph is not None and prot in graph:
            nbrs = set(graph.neighbors(prot))
            pw_nbrs = nbrs & pw_members
            degree = len(nbrs)
            pw_size = len(pw_members)

            if degree == 0 or pw_size == 0:
                prob = 0.05
            else:
                jaccard = len(pw_nbrs) / len(nbrs | pw_members)
                overlap_ratio = len(pw_nbrs) / min(pw_size, 10)
                mean_conf = np.mean([graph[prot][n].get("weight", 0.7) for n in pw_nbrs]) if pw_nbrs else 0.0
                prob = float(np.clip(0.5 * overlap_ratio + 0.3 * mean_conf + 0.2 * jaccard * 10, 0.0, 0.95))

            return {
                "protein_id": prot,
                "pathway_id": pathway_id,
                "pathway_name": pw["name"],
                "probability": round(prob, 4),
                "status": "inferred_candidate" if prob >= 0.50 else "non_member",
                "direct_connections": len(pw_nbrs),
                "connecting_partners": sorted(list(pw_nbrs)),
                "confidence_score": round(prob, 3)
            }

        return {
            "protein_id": prot,
            "pathway_id": pathway_id,
            "pathway_name": pw["name"],
            "probability": 0.10,
            "status": "unconnected",
            "confidence_score": 0.10
        }


class PathwayReconstructor:
    """Reconstructs missing pathway components and infers missing bridging edges (gap filling)."""

    def reconstruct_pathway(
        self,
        pathway_id: str,
        interactome_graph: nx.Graph,
        reactome_adapter: Optional[ReactomeAdapter] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Identify high-probability missing pathway members and missing bridging interactions.
        """
        reactome = reactome_adapter or ReactomeAdapter()
        pw = reactome.get_pathway(pathway_id)
        if not pw:
            return {"pathway_id": pathway_id, "error": "Pathway not found"}

        pw_members = set(pw["proteins"]) & set(interactome_graph.nodes())
        if len(pw_members) < 2:
            return {
                "pathway_id": pathway_id,
                "name": pw["name"],
                "missing_candidates": [],
                "suggested_bridges": []
            }

        # 1. Candidate proteins that interact with multiple pathway members
        candidate_scores = {}
        for node in interactome_graph.nodes():
            if node in pw_members:
                continue
            nbrs = set(interactome_graph.neighbors(node))
            overlap = nbrs & pw_members
            if len(overlap) >= 2:
                # Score by connectivity and interaction strength
                score = sum(interactome_graph[node][n].get("weight", 0.7) for n in overlap)
                candidate_scores[node] = {
                    "protein": node,
                    "connected_pathway_nodes": sorted(list(overlap)),
                    "pathway_connectivity": len(overlap),
                    "reconstruction_score": round(score, 3)
                }

        sorted_candidates = sorted(candidate_scores.values(), key=lambda x: -x["reconstruction_score"])[:top_k]

        # 2. Suggested bridges: find shortest paths between disconnected components of the pathway
        subgraph = interactome_graph.subgraph(pw_members)
        components = list(nx.connected_components(subgraph))
        suggested_bridges = []

        if len(components) > 1:
            for i in range(len(components) - 1):
                c1 = list(components[i])
                c2 = list(components[i + 1])
                # Find shortest path in full interactome
                try:
                    p = nx.shortest_path(interactome_graph, c1[0], c2[0], weight=lambda u, v, d: 1.0 - d.get("weight", 0.7))
                    if len(p) > 2:
                        suggested_bridges.append({
                            "source_component_node": c1[0],
                            "target_component_node": c2[0],
                            "bridging_path": p,
                            "bridge_intermediates": p[1:-1]
                        })
                except Exception:
                    pass

        return {
            "pathway_id": pathway_id,
            "name": pw["name"],
            "current_members_count": len(pw["proteins"]),
            "missing_candidates": sorted_candidates,
            "suggested_bridges": suggested_bridges
        }
