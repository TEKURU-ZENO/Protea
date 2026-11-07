"""State Fidelity Evaluator measuring accuracy against held-out biological observations."""

from __future__ import annotations

import math
from typing import Dict, List, Optional
from ai.digital_twin.schema import MolecularState


class StateFidelityEvaluator:
    """Measures Mean Absolute Error, RMSE, and Spearman correlation on held-out state values."""

    def evaluate(
        self,
        predicted_states: Dict[str, MolecularState],
        held_out_observations: Dict[str, float],
        feature: str = "gene_expression"
    ) -> Dict[str, float]:
        """Compares predicted/estimated molecular values with held-out experimental ground truth."""
        pairs: List[tuple[float, float]] = []

        for entity, true_val in held_out_observations.items():
            st = predicted_states.get(entity)
            if not st:
                continue
            pred_val = getattr(st, feature, None)
            if pred_val is not None:
                pairs.append((pred_val, true_val))

        if not pairs:
            return {"mae": 0.0, "rmse": 0.0, "spearman_rho": 1.0, "evaluated_samples": 0}

        n = len(pairs)
        mae = sum(abs(p - t) for p, t in pairs) / n
        rmse = math.sqrt(sum((p - t) ** 2 for p, t in pairs) / n)

        # Approximate Spearman correlation via rank differences
        sorted_pred = sorted(range(n), key=lambda i: pairs[i][0])
        sorted_true = sorted(range(n), key=lambda i: pairs[i][1])

        rank_p = [0] * n
        rank_t = [0] * n
        for r, i in enumerate(sorted_pred):
            rank_p[i] = r
        for r, i in enumerate(sorted_true):
            rank_t[i] = r

        d_sq_sum = sum((rank_p[i] - rank_t[i]) ** 2 for i in range(n))
        spearman = 1.0 - (6.0 * d_sq_sum) / max(1.0, n * (n ** 2 - 1)) if n > 1 else 1.0

        return {
            "mae": round(mae, 3),
            "rmse": round(rmse, 3),
            "spearman_rho": round(spearman, 3),
            "evaluated_samples": n
        }
