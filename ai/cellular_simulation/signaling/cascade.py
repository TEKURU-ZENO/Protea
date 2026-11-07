"""Multi-tier signaling cascade kinetics and signal propagation metrics."""

from typing import Dict, List, Tuple
import numpy as np
from ai.cellular_simulation.schema import Trajectory


class SignalingCascadeAnalyzer:
    """Analyzes signal amplification, propagation speed, and attenuation across cascade tiers."""

    @staticmethod
    def calculate_amplification_and_delay(
        trajectory: Trajectory,
        tiers: List[str], # e.g. ["Raf_star", "MEK_star", "ERK_star"]
    ) -> Dict[str, Dict[str, float]]:
        """Calculate peak amplitude, time-to-peak, and half-activation delay for each tier."""
        results = {}
        times = np.array(trajectory.times)

        for tier in tiers:
            if tier not in trajectory.species_trajectories:
                continue

            concs = np.array(trajectory.species_trajectories[tier])
            peak_val = float(np.max(concs))
            peak_idx = int(np.argmax(concs))
            peak_time = float(times[peak_idx])

            # Half-activation time (t_half)
            half_peak = 0.5 * peak_val
            half_indices = np.where(concs >= half_peak)[0]
            t_half = float(times[half_indices[0]]) if len(half_indices) > 0 else 0.0

            # Area under curve (integral of signal)
            trapz_fn = getattr(np, "trapezoid", getattr(np, "trapz", None))
            auc = float(trapz_fn(concs, times)) if len(times) > 1 and trapz_fn else 0.0

            results[tier] = {
                "peak_concentration": peak_val,
                "time_to_peak_seconds": peak_time,
                "t_half_activation_seconds": t_half,
                "area_under_curve": auc,
            }

        return results
