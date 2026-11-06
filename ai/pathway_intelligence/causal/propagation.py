"""
PROTEA PaIE - Network Propagation & Signaling Cascade Traversal
Implements Random Walk with Restart (RWR) and Yen's K-Shortest Paths for signaling chains.
"""

from typing import List, Dict, Set, Optional, Any
import numpy as np
import networkx as nx
from itertools import islice
import logging

logger = logging.getLogger("ai.pathway_intelligence.causal.propagation")

class NetworkPropagationEngine:
    """Simulates biological signal decay and network diffusion via Random Walk with Restart."""

    def __init__(self, restart_prob: float = 0.3, max_iter: int = 100, tol: float = 1e-6):
        self.restart_prob = restart_prob
        self.max_iter = max_iter
        self.tol = tol

    def propagate(
        self,
        seed_nodes: List[str],
        graph: nx.Graph,
        node_weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, float]:
        """
        Execute RWR starting from seed nodes.
        p_{t+1} = (1 - r) * W * p_t + r * p_0
        """
        nodes = list(graph.nodes())
        n = len(nodes)
        if n == 0:
            return {}

        node_to_idx = {node: i for i, node in enumerate(nodes)}

        # Initial probability vector p_0
        p0 = np.zeros(n, dtype=float)
        seeds_found = 0
        for s in seed_nodes:
            s_up = s.upper()
            if s_up in node_to_idx:
                w = node_weights.get(s_up, 1.0) if node_weights else 1.0
                p0[node_to_idx[s_up]] = w
                seeds_found += 1

        if seeds_found == 0:
            return {node: 1.0 / n for node in nodes}

        p0 /= np.sum(p0) # Normalize

        # Transition matrix W (column-normalized adjacency)
        adj = nx.to_numpy_array(graph, nodelist=nodes, weight="weight")
        col_sum = adj.sum(axis=0)
        col_sum[col_sum == 0] = 1.0
        W = adj / col_sum

        # Power iteration
        p = p0.copy()
        r = self.restart_prob

        for _ in range(self.max_iter):
            p_next = (1.0 - r) * np.dot(W, p) + r * p0
            if np.linalg.norm(p_next - p, ord=1) < self.tol:
                p = p_next
                break
            p = p_next

        return {nodes[i]: round(float(p[i]), 6) for i in range(n)}


class SignalingCascadeTracer:
    """Traces directed signaling chains and Yen's K-Shortest Paths between proteins."""

    def find_k_shortest_paths(
        self,
        source: str,
        target: str,
        graph: nx.Graph,
        k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Extract top K shortest paths using Yen's algorithm.
        Edge cost = -log(confidence) or 1.0 - confidence.
        """
        src = source.upper()
        tgt = target.upper()

        if src not in graph or tgt not in graph:
            return []

        def weight_fn(u, v, d):
            conf = d.get("weight", d.get("confidence", 0.75))
            return max(0.01, 1.0 - conf)

        try:
            generator = nx.shortest_simple_paths(graph, src, tgt, weight=weight_fn)
            paths = list(islice(generator, k))
            results = []
            for rank, p in enumerate(paths, start=1):
                # Calculate cumulative confidence
                edge_confs = []
                for i in range(len(p) - 1):
                    c = graph[p[i]][p[i + 1]].get("weight", graph[p[i]][p[i + 1]].get("confidence", 0.8))
                    edge_confs.append(c)

                results.append({
                    "rank": rank,
                    "path": p,
                    "length": len(p) - 1,
                    "average_confidence": round(float(np.mean(edge_confs)), 3) if edge_confs else 1.0,
                    "min_confidence": round(float(np.min(edge_confs)), 3) if edge_confs else 1.0
                })
            return results
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return []
