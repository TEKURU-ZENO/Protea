"""
PROTEA PaIE - Evaluation Metrics & Benchmarks
Scientific validation metrics for community detection, pathway prediction, and causal reasoning.
"""

from typing import List, Dict, Set, Any
import numpy as np
import networkx as nx

def calculate_modularity(graph: nx.Graph, communities: List[Set[str]], weight: str = "weight") -> float:
    """Calculate Newman-Girvan modularity Q for a community partition."""
    try:
        if len(communities) <= 1 or graph.number_of_edges() == 0:
            return 0.0
        return float(nx.community.modularity(graph, communities, weight=weight))
    except Exception:
        return 0.0

def calculate_conductance(graph: nx.Graph, community: Set[str], weight: str = "weight") -> float:
    """Calculate conductance of a community subnetwork."""
    try:
        if len(community) == 0 or len(community) == graph.number_of_nodes():
            return 0.0
        return float(nx.conductance(graph, community, weight=weight))
    except Exception:
        return 0.0

def precision_at_k(actual: List[str], predicted: List[str], k: int = 5) -> float:
    """Precision at rank K for pathway membership prediction."""
    if not actual or not predicted:
        return 0.0
    top_k = predicted[:k]
    hits = sum(1 for p in top_k if p in actual)
    return hits / min(k, len(predicted))

def recall_at_k(actual: List[str], predicted: List[str], k: int = 5) -> float:
    """Recall at rank K for pathway membership prediction."""
    if not actual or not predicted:
        return 0.0
    top_k = predicted[:k]
    hits = sum(1 for p in top_k if p in actual)
    return hits / len(actual)

def mean_reciprocal_rank(actual: List[str], predicted: List[str]) -> float:
    """Mean Reciprocal Rank (MRR) of first correct pathway member."""
    if not actual or not predicted:
        return 0.0
    actual_set = set(actual)
    for rank, p in enumerate(predicted, start=1):
        if p in actual_set:
            return 1.0 / rank
    return 0.0

def causal_direction_accuracy(ground_truth: List[Dict[str, str]], predictions: List[Dict[str, str]]) -> float:
    """
    Direction accuracy against curated evidence (activates, inhibits, etc.)
    Each item: {"source": str, "target": str, "direction": str}
    """
    if not ground_truth or not predictions:
        return 0.0

    gt_map = {(item["source"], item["target"]): item["direction"] for item in ground_truth}
    correct = 0
    total = 0

    for pred in predictions:
        pair = (pred["source"], pred["target"])
        if pair in gt_map:
            total += 1
            if gt_map[pair] == pred.get("direction"):
                correct += 1

    return correct / total if total > 0 else 0.0
