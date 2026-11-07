"""Phosphorylation-dephosphorylation covalent modification cycles."""

import numpy as np
from typing import Tuple


class PhosphorylationCycle:
    """Goldbeter-Koshland covalent modification cycle kinetics."""

    @staticmethod
    def goldbeter_koshland_analytical(
        v1: float,
        v2: float,
        J1: float,
        J2: float,
    ) -> float:
        """Exact Goldbeter-Koshland (1981) function for steady-state fraction of modified substrate.
        
        Args:
            v1: Vmax_kinase * [Kinase]
            v2: Vmax_phosphatase * [Phosphatase]
            J1: Km1 / W_total (relative Michaelis constant for kinase)
            J2: Km2 / W_total (relative Michaelis constant for phosphatase)
        
        Returns:
            fraction: W_star / W_total in [0, 1]
        """
        B = v2 - v1 + v2 * J1 + v1 * J2
        discriminant = B * B - 4.0 * (v2 - v1) * v1 * J2
        if discriminant < 0:
            discriminant = 0.0

        denom = B + np.sqrt(discriminant)
        if denom <= 0:
            return 0.0

        fraction = (2.0 * v1 * J2) / denom
        return float(np.clip(fraction, 0.0, 1.0))

    @staticmethod
    def rate_equations(
        w: float,
        w_star: float,
        vmax1: float,
        km1: float,
        vmax2: float,
        km2: float,
    ) -> Tuple[float, float]:
        """Differential rates dw/dt and dw_star/dt."""
        v_phospho = (vmax1 * w) / (km1 + w) if w > 0 else 0.0
        v_dephospho = (vmax2 * w_star) / (km2 + w_star) if w_star > 0 else 0.0

        dw_dt = v_dephospho - v_phospho
        dw_star_dt = v_phospho - v_dephospho
        return dw_dt, dw_star_dt
