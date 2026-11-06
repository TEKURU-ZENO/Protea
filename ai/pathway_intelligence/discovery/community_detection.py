"""
PROTEA PaIE - Community Discovery & Functional Modularity
Implements Louvain, Leiden, Markov Cluster Algorithm (MCL), and WCC clustering.
"""

from typing import Dict, List, Set, Optional, Any
import numpy as np
import networkx as nx
import logging
from ai.pathway_intelligence.registry import paie_registry
from ai.pathway_intelligence.evaluation.metrics import calculate_modularity

logger = logging.getLogger("ai.pathway_intelligence.discovery.community")

@paie_registry.register_community_detector("louvain")
class LouvainDetector:
    """Louvain community detection optimizing Newman-Girvan modularity."""

    def __init__(self, resolution: float = 1.0, seed: int = 42):
        self.resolution = resolution
        self.seed = seed

    def detect(self, graph: nx.Graph) -> List[Set[str]]:
        """Partition graph into modular communities using Louvain algorithm."""
        if graph.number_of_nodes() == 0:
            return []
        if graph.number_of_edges() == 0:
            return [{node} for node in graph.nodes()]

        try:
            # NetworkX built-in community.louvain_communities
            communities = nx.community.louvain_communities(
                graph,
                weight="weight",
                resolution=self.resolution,
                seed=self.seed
            )
            return sorted(communities, key=lambda c: len(c), reverse=True)
        except Exception as e:
            logger.warning(f"Louvain execution failed: {e}. Falling back to greedy modularity.")
            return sorted(nx.community.greedy_modularity_communities(graph), key=lambda c: len(c), reverse=True)


@paie_registry.register_community_detector("leiden")
class LeidenDetector:
    """Leiden community detection guaranteeing well-connected communities."""

    def __init__(self, resolution: float = 1.0, seed: int = 42):
        self.resolution = resolution
        self.seed = seed

    def detect(self, graph: nx.Graph) -> List[Set[str]]:
        """Execute Leiden partition (or refined modularity optimization)."""
        # If igraph / leidenalg is available, use it; otherwise use refined modularity
        try:
            import igraph as ig
            import leidenalg

            # Convert networkx to igraph
            nodes = list(graph.nodes())
            node_map = {n: i for i, n in enumerate(nodes)}
            edges = [(node_map[u], node_map[v]) for u, v in graph.edges()]
            weights = [graph[u][v].get("weight", 1.0) for u, v in graph.edges()]

            ig_graph = ig.Graph(n=len(nodes), edges=edges)
            ig_graph.es["weight"] = weights

            part = leidenalg.find_partition(
                ig_graph,
                leidenalg.ModularityVertexPartition,
                weights="weight",
                seed=self.seed
            )
            communities = [set(nodes[i] for i in cluster) for cluster in part]
            return sorted(communities, key=lambda c: len(c), reverse=True)
        except ImportError:
            # High-performance NetworkX fallback
            detector = LouvainDetector(resolution=self.resolution, seed=self.seed)
            return detector.detect(graph)


@paie_registry.register_community_detector("mcl")
class MarkovClusterAlgorithm:
    """Markov Cluster Algorithm (MCL) simulating random flow expansion and inflation."""

    def __init__(self, expansion: int = 2, inflation: float = 2.0, max_iter: int = 80):
        self.expansion = expansion
        self.inflation = inflation
        self.max_iter = max_iter

    def detect(self, graph: nx.Graph) -> List[Set[str]]:
        """Simulate stochastic flow on the adjacency matrix to detect protein complexes."""
        nodes = list(graph.nodes())
        n = len(nodes)
        if n == 0:
            return []
        if n == 1:
            return [{nodes[0]}]

        # Adjacency matrix with self-loops
        adj = nx.to_numpy_array(graph, nodelist=nodes, weight="weight")
        np.fill_diagonal(adj, 1.0)

        # Normalize columns (transition matrix)
        col_sum = adj.sum(axis=0)
        col_sum[col_sum == 0] = 1.0
        M = adj / col_sum

        for _ in range(self.max_iter):
            M_old = M.copy()
            # 1. Expand: power of matrix
            M = np.linalg.matrix_power(M, self.expansion)
            # 2. Inflate: element-wise power & re-normalize
            M = np.power(M, self.inflation)
            c_sum = M.sum(axis=0)
            c_sum[c_sum == 0] = 1.0
            M = M / c_sum

            # Check convergence
            if np.allclose(M, M_old, atol=1e-5):
                break

        # Extract attractor clusters
        clusters = {}
        for i in range(n):
            attractor = int(np.argmax(M[:, i]))
            if attractor not in clusters:
                clusters[attractor] = set()
            clusters[attractor].add(nodes[i])

        return sorted(list(clusters.values()), key=lambda c: len(c), reverse=True)


@paie_registry.register_community_detector("wcc")
class WCCDetector:
    """Weakly Connected Components detector."""

    def detect(self, graph: nx.Graph) -> List[Set[str]]:
        return sorted(list(nx.connected_components(graph)), key=lambda c: len(c), reverse=True)
