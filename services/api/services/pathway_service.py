"""
PROTEA API - Pathway Intelligence Service Layer
Orchestrates PaIE operations for API routers.
"""

from typing import List, Dict, Optional, Any
import networkx as nx
import logging

from ai.pathway_intelligence.ingestion.reactome import ReactomeAdapter
from ai.pathway_intelligence.ingestion.kegg import KEGGAdapter, WikiPathwaysAdapter
from ai.pathway_intelligence.annotation.functional_annotation import annotation_manager, localization_mapper
from ai.pathway_intelligence.annotation.gene_ontology import go_engine
from ai.pathway_intelligence.enrichment.ora import ORAEngine
from ai.pathway_intelligence.enrichment.gsea import GSEAEngine
from ai.pathway_intelligence.discovery.community_detection import LouvainDetector, MarkovClusterAlgorithm, LeidenDetector
from ai.pathway_intelligence.discovery.novel_pathways import DeNovoPathwayDiscoveryEngine
from ai.pathway_intelligence.prediction.pathway_membership import PathwayMembershipPredictor, PathwayReconstructor
from ai.pathway_intelligence.causal.regulatory_reasoning import RegulatoryReasoningEngine
from ai.pathway_intelligence.causal.propagation import NetworkPropagationEngine, SignalingCascadeTracer
from ai.pathway_intelligence.evolution.ortholog_mapping import CrossSpeciesOrthologMapper, PathwayEvolutionAnalyzer
from ai.pathway_intelligence.explainability.evidence import EvidenceAggregator, ScientificExplanationGenerator

logger = logging.getLogger("services.api.pathway_service")

class PathwayService:
    """Core service managing pathway queries, discovery pipelines, and causal reasoning."""

    def __init__(self):
        self.reactome = ReactomeAdapter()
        self.kegg = KEGGAdapter()
        self.wikipathways = WikiPathwaysAdapter()
        self.ora = ORAEngine(background_size=20000)
        self.gsea = GSEAEngine(n_permutations=100)
        self.louvain = LouvainDetector()
        self.mcl = MarkovClusterAlgorithm()
        self.novelty = DeNovoPathwayDiscoveryEngine(self.reactome)
        self.membership = PathwayMembershipPredictor(self.reactome)
        self.reconstructor = PathwayReconstructor()
        self.regulatory = RegulatoryReasoningEngine()
        self.propagation = NetworkPropagationEngine()
        self.cascade_tracer = SignalingCascadeTracer()
        self.evolution = PathwayEvolutionAnalyzer()
        self.evidence = EvidenceAggregator()
        self.explainer = ScientificExplanationGenerator(self.evidence)

        # Baseline demo graph of human PPI
        self._interactome_graph = self._build_baseline_interactome()
        self._directed_causal_graph = self._build_baseline_causal_graph()

    def _build_baseline_interactome(self) -> nx.Graph:
        """Construct high-confidence baseline interactome for immediate standalone execution."""
        g = nx.Graph()
        edges = [
            ("TP53", "MDM2", 0.95), ("TP53", "BAX", 0.92), ("BAX", "BCL2", 0.90),
            ("BCL2", "CASP3", 0.85), ("CASP8", "CASP3", 0.94), ("CASP9", "CASP3", 0.96),
            ("EGFR", "GRB2", 0.98), ("GRB2", "SOS1", 0.95), ("SOS1", "KRAS", 0.93),
            ("KRAS", "BRAF", 0.91), ("BRAF", "MAP2K1", 0.94), ("MAP2K1", "MAPK1", 0.97),
            ("PIK3CA", "AKT1", 0.93), ("AKT1", "MTOR", 0.96), ("AKT1", "GSK3B", 0.88),
            ("AKT1", "FOXO3", 0.87), ("PTEN", "AKT1", 0.91), ("BRCA1", "BARD1", 0.99),
            ("BRCA1", "RAD51", 0.94), ("ATM", "CHEK2", 0.95), ("CHEK2", "TP53", 0.90),
            ("CDK1", "CCNB1", 0.98), ("CDK2", "CCNE1", 0.92), ("CDK4", "CCND1", 0.94),
            ("CDK4", "RB1", 0.93), ("RB1", "E2F1", 0.97), ("CDKN1A", "CDK2", 0.92)
        ]
        for u, v, w in edges:
            g.add_edge(u, v, weight=w)
        return g

    def _build_baseline_causal_graph(self) -> nx.DiGraph:
        """Construct directed causal graph with signed mechanisms."""
        dg = nx.DiGraph()
        directed_edges = [
            ("EGFR", "GRB2", "activates", 0.98),
            ("GRB2", "SOS1", "complex_formation", 0.95),
            ("SOS1", "KRAS", "activates", 0.93),
            ("KRAS", "BRAF", "activates", 0.91),
            ("BRAF", "MAP2K1", "phosphorylates", 0.94),
            ("MAP2K1", "MAPK1", "phosphorylates", 0.97),
            ("PIK3CA", "AKT1", "activates", 0.93),
            ("PTEN", "AKT1", "inhibits", 0.91),
            ("AKT1", "MTOR", "activates", 0.96),
            ("AKT1", "FOXO3", "inhibits", 0.87),
            ("AKT1", "BAD", "inhibits", 0.88),
            ("TP53", "BAX", "activates", 0.92),
            ("BCL2", "BAX", "inhibits", 0.90),
            ("BAX", "CASP3", "activates", 0.89),
            ("ATM", "CHEK2", "phosphorylates", 0.95),
            ("CHEK2", "TP53", "phosphorylates", 0.90),
            ("CDKN1A", "CDK2", "inhibits", 0.92),
            ("CDK4", "RB1", "phosphorylates", 0.93),
            ("RB1", "E2F1", "inhibits", 0.97)
        ]
        for u, v, rel, w in directed_edges:
            dg.add_edge(u, v, type=rel, weight=w)
        return dg

    # Service operations
    def search_pathways(self, query: str) -> List[Dict[str, Any]]:
        q = query.lower()
        all_pws = self.reactome.list_all_pathways() + self.kegg.list_all_pathways()
        matches = []
        for pw in all_pws:
            if q in pw["name"].lower() or q in pw["id"].lower():
                matches.append(pw)
        return matches

    def get_pathway_by_id(self, pathway_id: str) -> Optional[Dict[str, Any]]:
        res = self.reactome.get_pathway(pathway_id)
        if not res:
            res = self.kegg.get_pathway(pathway_id)
        return res

    def run_enrichment(self, genes: List[str], p_cutoff: float = 0.05) -> List[Dict[str, Any]]:
        return self.ora.run_enrichment(genes, p_cutoff=p_cutoff)

    def discover_communities(self, algorithm: str = "louvain") -> List[Dict[str, Any]]:
        algo = algorithm.lower()
        if algo == "mcl":
            clusters = self.mcl.detect(self._interactome_graph)
        else:
            clusters = self.louvain.detect(self._interactome_graph)

        results = []
        for i, c in enumerate(clusters):
            results.append({
                "community_id": f"COMM_{i+1}",
                "size": len(c),
                "proteins": sorted(list(c)),
                "density": float(nx.density(self._interactome_graph.subgraph(c)))
            })
        return results

    def discover_dark_matter(self) -> List[Dict[str, Any]]:
        return self.novelty.discover_novel_pathways(self._interactome_graph)

    def predict_membership(self, protein_id: str, pathway_id: str) -> Dict[str, Any]:
        return self.membership.predict_membership(protein_id, pathway_id, self._interactome_graph)

    def reconstruct_pathway(self, pathway_id: str) -> Dict[str, Any]:
        return self.reconstructor.reconstruct_pathway(pathway_id, self._interactome_graph, self.reactome)

    def analyze_causality(self, path: List[str]) -> Dict[str, Any]:
        return self.regulatory.evaluate_cascade_causality(path, self._directed_causal_graph)

    def trace_signaling_cascade(self, source: str, target: str, k: int = 3) -> List[Dict[str, Any]]:
        return self.cascade_tracer.find_k_shortest_paths(source, target, self._interactome_graph, k=k)

    def run_cross_species_comparison(self, pathway_id: str) -> Dict[str, Any]:
        pw = self.get_pathway_by_id(pathway_id)
        if not pw:
            return {"error": "Pathway not found"}
        return self.evolution.compare_pathway_across_species(pw["id"], pw["name"], pw["proteins"])

    def get_evidence_for_pathway(self, pathway_id: str) -> Dict[str, Any]:
        pw = self.get_pathway_by_id(pathway_id)
        if not pw:
            return {"error": "Pathway not found"}
        prots = pw["proteins"]
        pair_evidences = []
        for i in range(len(prots)):
            for j in range(i + 1, min(len(prots), i + 4)):
                ev = self.evidence.get_evidence(prots[i], prots[j])
                pair_evidences.append({
                    "protein_a": prots[i],
                    "protein_b": prots[j],
                    "evidence": ev
                })
        return {
            "pathway_id": pathway_id,
            "pathway_name": pw["name"],
            "evidence_pairs": pair_evidences
        }

    def get_statistics(self) -> Dict[str, Any]:
        all_reactome = self.reactome.list_all_pathways()
        return {
            "curated_pathways_count": len(all_reactome) + len(self.kegg.list_all_pathways()),
            "total_annotated_proteins": len(set(p for pw in all_reactome for p in pw["proteins"])),
            "interactome_nodes": self._interactome_graph.number_of_nodes(),
            "interactome_edges": self._interactome_graph.number_of_edges(),
            "supported_species": ["human", "mouse", "zebrafish", "drosophila", "yeast"],
            "enrichment_algorithms": ["ORA (Hypergeometric)", "GSEA (Running Sum)", "GSVA"],
            "clustering_algorithms": ["Louvain", "Leiden", "MCL", "WCC"]
        }

pathway_service = PathwayService()
