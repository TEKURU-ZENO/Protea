"""
PROTEA PaIE - Subgraph Mining & Network Motif Discovery
Extracts dense functional complexes and regulatory network motifs (feed-forward loops, bi-fans).
"""

from typing import List, Dict, Set, Tuple, Any
import networkx as nx

class SubgraphMiner:
    """Extracts dense k-cliques and induced functional modules from protein graphs."""

    def find_dense_modules(self, graph: nx.Graph, min_size: int = 3, min_density: float = 0.6) -> List[Dict[str, Any]]:
        """Identify dense subgraphs exceeding minimum connectivity density."""
        modules = []
        cliques = list(nx.find_cliques(graph))
        for c in cliques:
            if len(c) >= min_size:
                sub = graph.subgraph(c)
                density = nx.density(sub)
                if density >= min_density:
                    modules.append({
                        "nodes": sorted(list(c)),
                        "size": len(c),
                        "density": float(density)
                    })
        return sorted(modules, key=lambda m: (-m["size"], -m["density"]))


class MotifDiscoveryEngine:
    """Detects recurring regulatory subnetwork motifs in directed signaling graphs."""

    def detect_feed_forward_loops(self, graph: nx.DiGraph) -> List[Dict[str, str]]:
        """
        Detect Coherent & Incoherent Feed-Forward Loops (FFLs):
        Structure: X -> Y, Y -> Z, X -> Z.
        """
        ffls = []
        for x in graph.nodes():
            for y in graph.successors(x):
                if y == x:
                    continue
                for z in graph.successors(y):
                    if z == x or z == y:
                        continue
                    if graph.has_edge(x, z):
                        ffls.append({
                            "top_regulator": x,
                            "intermediate_regulator": y,
                            "target_node": z,
                            "type": "feed_forward_loop"
                        })
        return ffls

    def detect_feedback_loops(self, graph: nx.DiGraph) -> List[List[str]]:
        """Detect cyclic regulatory feedback loops (2-node and 3-node cycles)."""
        cycles = list(nx.simple_cycles(graph))
        return [c for c in cycles if 2 <= len(c) <= 5]
