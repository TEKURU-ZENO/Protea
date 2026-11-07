"""
PROTEA Phase 10: Dose-Response Model
Simulates sigmoidal dose-response relationships using the Hill equation and computes IC50 fold shifts.
"""

from __future__ import annotations
import math
from typing import Dict, List, Any, Tuple
from ai.mutation_therapeutics.schema import DrugResponse


class DoseResponseModel:
    """Models sigmoidal pharmacological dose-response behavior."""

    @staticmethod
    def hill_equation(
        concentration: float,
        ic50: float,
        hill_coefficient: float = 1.0,
        e_min: float = 0.0,
        e_max: float = 100.0
    ) -> float:
        """
        Calculates percentage response at concentration c using 4-parameter logistic (4PL):
        E(c) = E_min + (E_max - E_min) / (1 + (IC50 / c)^h).
        """
        if concentration <= 0.0:
            return e_min
        ratio = (ic50 / concentration) ** hill_coefficient
        return e_min + (e_max - e_min) / (1.0 + ratio)

    @classmethod
    def compute_response_shift(
        cls,
        drug_id: str,
        target_id: str,
        wt_ic50_nm: float,
        mut_ic50_nm: float,
        hill_coefficient: float = 1.0
    ) -> DrugResponse:
        """
        Computes fold change in IC50 and assigns sensitivity phenotype:
        - Sensitive: fold change <= 2.0
        - Intermediate: 2.0 < fold change < 5.0
        - Resistant: fold change >= 5.0
        """
        fold_change = round(mut_ic50_nm / max(0.001, wt_ic50_nm), 2)

        if fold_change >= 5.0:
            phenotype = "resistant"
        elif fold_change > 2.0:
            phenotype = "intermediate"
        else:
            phenotype = "sensitive"

        return DrugResponse(
            drug_id=drug_id,
            target_id=target_id,
            wildtype_ic50_nm=wt_ic50_nm,
            mutant_ic50_nm=mut_ic50_nm,
            resistance_fold_change=fold_change,
            hill_coefficient=hill_coefficient,
            response_phenotype=phenotype
        )

    @classmethod
    def generate_dose_curve_points(
        cls,
        ic50_nm: float,
        hill_coefficient: float = 1.0,
        num_points: int = 10
    ) -> List[Dict[str, float]]:
        """Generates log-spaced concentration vs response points for plotting."""
        points: List[Dict[str, float]] = []
        # Span from 2 orders of magnitude below IC50 to 2 orders above
        log_ic50 = math.log10(max(0.1, ic50_nm))
        min_log = log_ic50 - 2.0
        max_log = log_ic50 + 2.0
        step = (max_log - min_log) / (num_points - 1)

        for i in range(num_points):
            c = 10 ** (min_log + (i * step))
            resp = cls.hill_equation(c, ic50_nm, hill_coefficient)
            points.append({"concentration_nm": round(c, 2), "inhibition_percent": round(resp, 2)})

        return points
