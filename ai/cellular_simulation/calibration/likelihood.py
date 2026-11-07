"""Objective functions and likelihood formulations for model calibration."""

from typing import Dict, List, Optional
import numpy as np


class CalibrationLikelihood:
    """Calculates objective discrepancy functions between simulated and experimental data."""

    @staticmethod
    def sum_of_squared_errors(
        simulated: Dict[str, List[float]], # species_id -> time-series values
        experimental: Dict[str, List[float]], # species_id -> matched time-series values
    ) -> float:
        """Compute unweighted Sum of Squared Errors (SSE)."""
        total_sse = 0.0
        for s_id, exp_vals in experimental.items():
            if s_id in simulated:
                sim_vals = np.array(simulated[s_id][:len(exp_vals)])
                exp_arr = np.array(exp_vals)
                total_sse += float(np.sum((sim_vals - exp_arr) ** 2))
        return total_sse

    @staticmethod
    def log_likelihood(
        simulated: Dict[str, List[float]],
        experimental: Dict[str, List[float]],
        sigma: float = 0.1,
    ) -> float:
        """Compute Gaussian log-likelihood given observation noise sigma."""
        sse = CalibrationLikelihood.sum_of_squared_errors(simulated, experimental)
        n_points = sum(len(v) for v in experimental.values())
        if n_points == 0:
            return 0.0

        log_lik = -0.5 * n_points * np.log(2.0 * np.pi * sigma**2) - (sse / (2.0 * sigma**2))
        return float(log_lik)
