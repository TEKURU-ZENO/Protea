"""Dose-response titration curve and IC50/EC50 estimation."""

from typing import Dict, List, Tuple
import numpy as np


class DoseResponseCurve:
    """Calculates pharmacology dose-response curves and extracts IC50/EC50 and Hill slope."""

    @staticmethod
    def fit_hill_equation(
        doses: List[float],
        responses: List[float],
    ) -> Dict[str, float]:
        """Fit 4-parameter logistic / Hill equation to dose-response data."""
        d_arr = np.array(doses)
        r_arr = np.array(responses)

        bottom = float(np.min(r_arr))
        top = float(np.max(r_arr))
        half_response = bottom + 0.5 * (top - bottom)

        # Estimate IC50 / EC50 by linear interpolation
        if top > bottom:
            # Sorted by dose
            idx = np.argsort(d_arr)
            d_sorted = d_arr[idx]
            r_sorted = r_arr[idx]
            ec50 = float(np.interp(half_response, r_sorted, d_sorted))
        else:
            ec50 = float(d_arr[len(d_arr) // 2])

        # Estimate Hill coefficient nH
        hill_slope = 1.0
        if len(d_arr) >= 4:
            # Approximate slope in log-space around EC50
            log_d = np.log10(np.maximum(1e-9, d_arr))
            norm_r = (r_arr - bottom) / max(1e-9, (top - bottom))
            mask = (norm_r > 0.1) & (norm_r < 0.9)
            if np.sum(mask) >= 2:
                # logit(y) = n * (log(x) - log(ec50))
                logit_r = np.log(norm_r[mask] / (1.0 - norm_r[mask]))
                delta_log_d = log_d[mask] - np.log10(max(1e-9, ec50))
                coeffs = np.polyfit(delta_log_d, logit_r, 1)
                hill_slope = float(np.clip(coeffs[0], 0.1, 10.0))

        return {
            "bottom": bottom,
            "top": top,
            "ec50_or_ic50": ec50,
            "hill_slope": hill_slope,
        }
