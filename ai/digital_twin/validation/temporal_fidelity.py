"""Temporal Fidelity Evaluator measuring dynamic trajectory forecasting error."""

from __future__ import annotations

import math
from typing import Dict, List
from ai.digital_twin.schema import TemporalObservation


class TemporalFidelityEvaluator:
    """Evaluates whether the digital twin captures observed longitudinal shifts over time."""

    def evaluate(
        self,
        predicted_timecourses: Dict[str, List[float]],
        held_out_timecourses: Dict[str, List[float]]
    ) -> Dict[str, float]:
        """Calculates trajectory forecasting RMSE and trajectory direction correlation."""
        errors: List[float] = []
        concordant_slopes = 0
        total_intervals = 0

        for entity, true_series in held_out_timecourses.items():
            pred_series = predicted_timecourses.get(entity, [])
            min_len = min(len(pred_series), len(true_series))
            for i in range(min_len):
                errors.append((pred_series[i] - true_series[i]) ** 2)

            for i in range(1, min_len):
                d_true = true_series[i] - true_series[i - 1]
                d_pred = pred_series[i] - pred_series[i - 1]
                if (d_true >= 0 and d_pred >= 0) or (d_true <= 0 and d_pred <= 0):
                    concordant_slopes += 1
                total_intervals += 1

        rmse = math.sqrt(sum(errors) / max(1, len(errors))) if errors else 0.0
        trajectory_corr = concordant_slopes / max(1, total_intervals) if total_intervals > 0 else 1.0

        return {
            "forecasting_rmse": round(rmse, 3),
            "trajectory_correlation": round(trajectory_corr, 3)
        }
