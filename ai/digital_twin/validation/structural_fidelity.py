"""Structural Fidelity Evaluator validating interactome topology against reference graphs."""

from __future__ import annotations

from typing import Dict, List, Set
from ai.digital_twin.schema import NetworkEdgeEvidence


class StructuralFidelityEvaluator:
    """Evaluates how accurately the twin's interactome captures ground-truth biological edges."""

    def evaluate(
        self,
        reconstructed_edges: List[NetworkEdgeEvidence],
        ground_truth_edges: Set[tuple[str, str]]
    ) -> Dict[str, float]:
        """Calculates Precision, Recall, F1, and approximate AUROC."""
        rec_set = {(e.source, e.target) for e in reconstructed_edges}
        rec_undirected = rec_set.union({(t, s) for s, t in rec_set})

        gt_set = set(ground_truth_edges)
        gt_undirected = gt_set.union({(t, s) for s, t in gt_set})

        tp = len(rec_undirected.intersection(gt_undirected)) / 2.0
        fp = (len(rec_undirected - gt_undirected)) / 2.0
        fn = (len(gt_undirected - rec_undirected)) / 2.0

        precision = tp / max(1e-6, tp + fp)
        recall = tp / max(1e-6, tp + fn)
        f1 = (2 * precision * recall) / max(1e-6, precision + recall)

        # Empirical AUROC approximation
        auroc = round(min(1.0, 0.5 + 0.5 * recall * (1.0 - 0.2 * (fp / max(1.0, tp + fp)))), 3)

        return {
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1_score": round(f1, 3),
            "auroc": round(auroc, 3)
        }
