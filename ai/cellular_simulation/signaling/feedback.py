"""Feedback motif dynamics: oscillations, adaptation, and bistability."""

from typing import Any, Dict, List, Tuple
import numpy as np


class FeedbackAnalyzer:
    """Detects and characterizes dynamical regimes (oscillations, adaptation, bistability)."""

    @staticmethod
    def detect_oscillations(
        times: List[float],
        values: List[float],
        min_peaks: int = 2,
    ) -> Dict[str, Any]:
        """Detect periodic oscillations and compute period and amplitude."""
        from scipy.signal import find_peaks

        vals = np.array(values)
        t = np.array(times)

        # Detect local maxima
        peaks, props = find_peaks(vals, prominence=0.05 * (np.max(vals) - np.min(vals) + 1e-9))

        is_oscillatory = len(peaks) >= min_peaks
        period = 0.0
        frequency = 0.0
        mean_amplitude = 0.0

        if is_oscillatory:
            peak_times = t[peaks]
            periods = np.diff(peak_times)
            if len(periods) > 0:
                period = float(np.mean(periods))
                frequency = float(1.0 / period) if period > 0 else 0.0

            peak_values = vals[peaks]
            mean_amplitude = float(np.mean(peak_values) - np.min(vals))

        return {
            "is_oscillatory": is_oscillatory,
            "peak_count": len(peaks),
            "period_seconds": period,
            "frequency_hz": frequency,
            "amplitude": mean_amplitude,
        }

    @staticmethod
    def calculate_adaptation_index(
        values: List[float],
    ) -> float:
        """Measure sensory adaptation: 1.0 = perfect adaptation back to baseline."""
        vals = np.array(values)
        if len(vals) < 3:
            return 0.0

        v_init = vals[0]
        v_peak = np.max(vals)
        v_final = vals[-1]

        dynamic_range = v_peak - v_init
        if dynamic_range <= 1e-9:
            return 1.0

        # Adaptation index: fraction of response returned to baseline
        adaptation = (v_peak - v_final) / dynamic_range
        return float(np.clip(adaptation, 0.0, 1.0))
