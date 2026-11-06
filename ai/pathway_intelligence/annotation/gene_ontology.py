"""
PROTEA PaIE - Gene Ontology (GO) Graph Parser & Semantic Engine
Models GO DAG structures across Biological Process (BP), Molecular Function (MF), and Cellular Component (CC).
"""

from typing import Dict, List, Set, Optional, Any
import networkx as nx

class GeneOntologyEngine:
    """Directed Acyclic Graph (DAG) representation of Gene Ontology terms and relationships."""

    def __init__(self):
        self.dag = nx.DiGraph()
        self._terms: Dict[str, Dict[str, Any]] = {}
        self._initialize_core_terms()

    def _initialize_core_terms(self):
        """Populate core standard Gene Ontology terms across all three domains."""
        core_terms = [
            # Biological Process (BP)
            {"id": "GO:0008150", "name": "biological_process", "namespace": "BP", "parents": []},
            {"id": "GO:0009987", "name": "cellular process", "namespace": "BP", "parents": ["GO:0008150"]},
            {"id": "GO:0006915", "name": "apoptotic process", "namespace": "BP", "parents": ["GO:0009987"]},
            {"id": "GO:0007049", "name": "cell cycle", "namespace": "BP", "parents": ["GO:0009987"]},
            {"id": "GO:0006281", "name": "DNA repair", "namespace": "BP", "parents": ["GO:0009987"]},
            {"id": "GO:0007165", "name": "signal transduction", "namespace": "BP", "parents": ["GO:0009987"]},
            {"id": "GO:0000165", "name": "MAPK cascade", "namespace": "BP", "parents": ["GO:0007165"]},
            {"id": "GO:0006468", "name": "protein phosphorylation", "namespace": "BP", "parents": ["GO:0009987"]},
            # Molecular Function (MF)
            {"id": "GO:0003674", "name": "molecular_function", "namespace": "MF", "parents": []},
            {"id": "GO:0005515", "name": "protein binding", "namespace": "MF", "parents": ["GO:0003674"]},
            {"id": "GO:0003677", "name": "DNA binding", "namespace": "MF", "parents": ["GO:0003674"]},
            {"id": "GO:0004672", "name": "protein kinase activity", "namespace": "MF", "parents": ["GO:0003674"]},
            {"id": "GO:0004674", "name": "protein serine/threonine kinase activity", "namespace": "MF", "parents": ["GO:0004672"]},
            {"id": "GO:0008233", "name": "peptidase activity", "namespace": "MF", "parents": ["GO:0003674"]},
            # Cellular Component (CC)
            {"id": "GO:0005575", "name": "cellular_component", "namespace": "CC", "parents": []},
            {"id": "GO:0005623", "name": "cell", "namespace": "CC", "parents": ["GO:0005575"]},
            {"id": "GO:0005634", "name": "nucleus", "namespace": "CC", "parents": ["GO:0005623"]},
            {"id": "GO:0005829", "name": "cytosol", "namespace": "CC", "parents": ["GO:0005623"]},
            {"id": "GO:0005886", "name": "plasma membrane", "namespace": "CC", "parents": ["GO:0005623"]},
            {"id": "GO:0005739", "name": "mitochondrion", "namespace": "CC", "parents": ["GO:0005623"]},
        ]

        for term in core_terms:
            self.add_term(term["id"], term["name"], term["namespace"], term["parents"])

    def add_term(self, term_id: str, name: str, namespace: str, parents: List[str]):
        """Add a GO term to the DAG with parent relationship links."""
        self._terms[term_id] = {
            "id": term_id,
            "name": name,
            "namespace": namespace,
            "parents": parents
        }
        self.dag.add_node(term_id, name=name, namespace=namespace)
        for parent_id in parents:
            # Directed edge from child -> parent (is_a relation)
            self.dag.add_edge(term_id, parent_id, relation="is_a")

    def get_term(self, term_id: str) -> Optional[Dict[str, Any]]:
        return self._terms.get(term_id)

    def get_ancestors(self, term_id: str) -> Set[str]:
        """Retrieve all ancestor terms up to the root via transitive closure."""
        if term_id not in self.dag:
            return set()
        return nx.descendants(self.dag, term_id)  # Since edges point child -> parent

    def get_descendants(self, term_id: str) -> Set[str]:
        """Retrieve all specialized child terms."""
        if term_id not in self.dag:
            return set()
        return nx.ancestors(self.dag, term_id)

    def semantic_similarity(self, term_a: str, term_b: str) -> float:
        """Calculate Jaccard semantic similarity over shared ancestor sets."""
        if term_a == term_b:
            return 1.0
        anc_a = self.get_ancestors(term_a) | {term_a}
        anc_b = self.get_ancestors(term_b) | {term_b}
        intersection = anc_a & anc_b
        union = anc_a | anc_b
        return len(intersection) / len(union) if union else 0.0

# Singleton instance
go_engine = GeneOntologyEngine()
