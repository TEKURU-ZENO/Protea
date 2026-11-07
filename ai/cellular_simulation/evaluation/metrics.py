"""Numerical and biological evaluation metrics for simulation systems."""

from typing import Dict, List
import numpy as np


class SimulationMetrics:
    """Calculates quantitative performance, physical conservation, and stability metrics."""

    @staticmethod
    def calculate_trajectory_metrics(
        times: List[float],
        trajectories: Dict[str, List[float]],
    ) -> Dict[str, float]:
        """Compute summary statistics across simulated trajectories."""
        n_steps = len(times)
        total_mass_end = sum(series[-1] for series in trajectories.values()) if n_steps > 0 else 0.0
        peak_conc = max(max(series) for series in trajectories.values()) if trajectories else 0.0

        return {
            "total_time_points": float(n_steps),
            "simulated_duration": float(times[-1] - times[0]) if n_steps > 1 else 0.0,
            "total_terminal_mass": float(total_mass_end),
            "peak_concentration_observed": float(peak_conc),
        }
