"""Quantitative validation against empirical experimental time-series."""

from typing import Dict, List, Tuple
import numpy as np


class ExperimentalDataComparator:
    """Evaluates trajectory goodness-of-fit against empirical wet-lab measurements."""

    @staticmethod
    def evaluate_fit(
        simulated_values: List[float],
        experimental_values: List[float],
    ) -> Dict[str, float]:
        """Compute RMSE, Pearson correlation r, and R^2 between simulation and experiment."""
        y_sim = np.array(simulated_values)
        y_exp = np.array(experimental_values)

        n = min(len(y_sim), len(y_exp))
        if n < 2:
            return {"rmse": 0.0, "pearson_r": 1.0, "r_squared": 1.0}

        y_s = y_sim[:n]
        y_e = y_exp[:n]

        # RMSE
        rmse = float(np.sqrt(np.mean((y_s - y_e) ** 2)))

        # Pearson r
        if np.std(y_s) > 1e-12 and np.std(y_e) > 1e-12:
            pearson_r = float(np.corrcoef(y_s, y_e)[0, 1])
        else:
            pearson_r = 1.0 if np.allclose(y_s, y_e) else 0.0

        # R^2
        ss_res = np.sum((y_e - y_s) ** 2)
        ss_tot = np.sum((y_e - np.mean(y_e)) ** 2)
        r_squared = float(1.0 - (ss_res / max(1e-12, ss_tot)))

        return {
            "rmse": rmse,
            "pearson_r": pearson_r,
            "r_squared": r_squared,
        }
