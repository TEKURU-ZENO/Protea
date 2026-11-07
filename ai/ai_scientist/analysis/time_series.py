"""Dynamic time-series trajectory comparative analyzer."""

from typing import Dict, List
import numpy as np


class TimeSeriesAnalyzer:
    """Analyzes trajectory dynamics, peak shifts, and area-under-the-curve differences."""

    @staticmethod
    def compare_trajectories(
        times: List[float],
        baseline_series: List[float],
        perturbed_series: List[float],
    ) -> Dict[str, float]:
        """Compute trajectory integrals (AUC), peak values, and signal attenuation."""
        t_arr = np.array(times)
        b_arr = np.array(baseline_series)
        p_arr = np.array(perturbed_series)

        trapz_fn = getattr(np, "trapezoid", getattr(np, "trapz", None))
        auc_base = float(trapz_fn(b_arr, t_arr)) if trapz_fn else 0.0
        auc_pert = float(trapz_fn(p_arr, t_arr)) if trapz_fn else 0.0

        auc_ratio = (auc_pert / max(1e-9, auc_base)) if auc_base > 0 else 0.0

        return {
            "baseline_auc": round(auc_base, 3),
            "perturbed_auc": round(auc_pert, 3),
            "auc_retention_ratio": round(auc_ratio, 3),
            "peak_reduction_percent": round((1.0 - (np.max(p_arr) / max(1e-9, np.max(b_arr)))) * 100.0, 2),
        }
