"""
PROTEA PaIE - De Novo Pathway Discovery & Biological "Dark Matter" Engine
Identifies novel unannotated functional modules and hypothesizes functions via Guilt-by-Association.
"""

from typing import List, Dict, Set, Optional, Any
import networkx as nx
import numpy as np
import logging
from ai.pathway_intelligence.discovery.community_detection import LouvainDetector
from ai.pathway_intelligence.annotation.functional_annotation import annotation_manager
from ai.pathway_intelligence.ingestion.reactome import ReactomeAdapter

logger = logging.getLogger("ai.pathway_intelligence.discovery.novel")

class DeNovoPathwayDiscoveryEngine:
    """Discovers uncharacterized 'dark matter' biological pathways and functional modules."""

    def __init__(self, reactome_adapter: Optional[ReactomeAdapter] = None):
        self.reactome = reactome_adapter or ReactomeAdapter()
        self.community_detector = LouvainDetector()

    def discover_novel_pathways(
        self,
        graph: nx.Graph,
        max_annotation_ratio: float = 0.25,
        min_cluster_size: int = 3,
        min_density: float = 0.50
    ) -> List[Dict[str, Any]]:
        """
        Uncover dark-matter candidate pathways:
        1. Clusters the interactome graph into dense modules.
        2. Evaluates reference database coverage (% of proteins in known Reactome pathways).
        3. Filters for modules with high topological density but low annotation coverage.
        4. Calculates functional coherence & predicts candidate pathway hypotheses.
        """
        communities = self.community_detector.detect(graph)
        candidates = []

        for i, comm in enumerate(communities):
            if len(comm) < min_cluster_size:
                continue

            subgraph = graph.subgraph(comm)
            density = float(nx.density(subgraph))
            if density < min_density:
                continue

            # Check annotation coverage
            annotated_proteins = []
            unannotated_proteins = []
            known_pathway_hits = set()

            for prot in comm:
                pws = self.reactome.get_pathways_for_protein(prot)
                if pws:
                    annotated_proteins.append(prot)
                    for pw in pws:
                        known_pathway_hits.add(pw["name"])
                else:
                    unannotated_proteins.append(prot)

            annotation_ratio = len(annotated_proteins) / len(comm)

            # Is this biological dark matter?
            if annotation_ratio <= max_annotation_ratio:
                # Infer candidate hypothesis using neighbor guilt-by-association
                inferred_hypothesis = self._infer_cluster_hypothesis(comm, graph)

                candidates.append({
                    "cluster_id": f"NOVEL-PW-{i+1:03d}",
                    "size": len(comm),
                    "density": density,
                    "annotation_ratio": round(annotation_ratio, 3),
                    "known_pathway_overlap": sorted(list(known_pathway_hits)),
                    "unannotated_members": sorted(unannotated_proteins),
                    "annotated_members": sorted(annotated_proteins),
                    "all_members": sorted(list(comm)),
                    "candidate_hypothesis": inferred_hypothesis,
                    "dark_matter_score": round((1.0 - annotation_ratio) * density, 3)
                })

        # Rank by dark matter score (highest density + lowest annotation coverage)
        candidates.sort(key=lambda c: -c["dark_matter_score"])
        return candidates

    def _infer_cluster_hypothesis(self, cluster_nodes: Set[str], full_graph: nx.Graph) -> str:
        """Infer potential biological function of uncharacterized cluster via guilt-by-association."""
        neighbor_terms = []
        for node in cluster_nodes:
            # Check 1-hop neighbors in the full interactome
            for nbr in full_graph.neighbors(node):
                terms = annotation_manager.get_terms_for_protein(nbr, propagate=False)
                for t in terms:
                    if t["namespace"] == "BP":
                        neighbor_terms.append(t["name"])

        if neighbor_terms:
            from collections import Counter
            counts = Counter(neighbor_terms)
            top_process, top_freq = counts.most_common(1)[0]
            return f"Hypothesized functional module linked to '{top_process}' (supported by {top_freq} interacting neighbors)"

        return "Novel uncharacterized protein complex; requires primary biochemical characterization."

    def predict_orphan_functions(self, orphan_protein: str, graph: nx.Graph) -> List[Dict[str, Any]]:
        """Predict GO biological processes for uncharacterized protein via guilt-by-association."""
        prot = orphan_protein.upper()
        if prot not in graph:
            return []

        neighbors = list(graph.neighbors(prot))
        if not neighbors:
            return []

        term_weights = {}
        for nbr in neighbors:
            edge_weight = graph[prot][nbr].get("weight", 0.75)
            nbr_terms = annotation_manager.get_terms_for_protein(nbr, propagate=False)
            for t in nbr_terms:
                tid = t["term_id"]
                if tid not in term_weights:
                    term_weights[tid] = {
                        "term_id": tid,
                        "name": t["name"],
                        "namespace": t["namespace"],
                        "score": 0.0,
                        "support_count": 0
                    }
                term_weights[tid]["score"] += edge_weight
                term_weights[tid]["support_count"] += 1

        results = list(term_weights.values())
        max_score = max((r["score"] for r in results), default=1.0)
        for r in results:
            r["confidence"] = round(r["score"] / max_score, 3)

        results.sort(key=lambda r: -r["confidence"])
        return results[:8]
