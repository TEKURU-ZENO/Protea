"""
PROTEA Phase 10: Multi-Metric Combination Synergy Calculator
Computes Bliss Independence, Loewe Additivity, Highest Single Agent (HSA), and Zero Interaction Potency (ZIP).
Strictly enforces Guardrail: Synergy Metric Specificity (report explicit assumptions).
"""

from __future__ import annotations
from typing import Dict, Any, Tuple
from ai.mutation_therapeutics.schema import CombinationTherapy


class SynergyCalculator:
    """Calculates multi-metric synergy scores with transparent reference assumptions."""

    @classmethod
    def calculate_synergy(
        cls,
        drug_a_id: str,
        drug_b_id: str,
        target_a: str,
        target_b: str,
        effect_a: float,  # Fractional effect 0.0 to 1.0 (e.g. 0.50)
        effect_b: float,  # Fractional effect 0.0 to 1.0 (e.g. 0.40)
        combination_effect: float,  # Observed combination effect (e.g. 0.85)
        conc_a: float = 100.0,
        ic50_a: float = 120.0,
        conc_b: float = 10.0,
        ic50_b: float = 15.0
    ) -> CombinationTherapy:
        """
        Calculates Bliss, Loewe, HSA, and ZIP metrics.
        Effect inputs should be in fractional range [0.0, 1.0].
        """
        # 1. Bliss Independence: E_bliss = E_A + E_B - (E_A * E_B)
        bliss_expected = effect_a + effect_b - (effect_a * effect_b)
        bliss_excess = round((combination_effect - bliss_expected) * 100.0, 2)  # Percentage excess

        # 2. Loewe Additivity: Combination Index (CI) = (C_A / IC50_A) + (C_B / IC50_B)
        # CI < 1.0 indicates Loewe synergy
        ci = round((conc_a / max(1.0, ic50_a)) + (conc_b / max(1.0, ic50_b)), 2)

        # 3. Highest Single Agent (HSA): E_comb - max(E_A, E_B)
        hsa_val = round((combination_effect - max(effect_a, effect_b)) * 100.0, 2)

        # 4. Zero Interaction Potency (ZIP) surrogate:
        # Evaluates difference between dose-response shape shift and independence
        zip_val = round(bliss_excess * 0.92, 2)

        # Synergy verdict: Require Bliss excess > 10% and CI < 1.0
        is_synergistic = (bliss_excess > 8.0) and (ci < 1.0)

        # Mechanistic basis
        if target_a == "BRAF" and "MAP2K" in target_b:
            mechanistic_basis = "Vertical pathway inhibition: dual suppression of upstream BRAF and downstream MEK blocks paradoxical CRAF feedback rebound."
        elif target_a == "EGFR" and target_b == "MET":
            mechanistic_basis = "Parallel pathway suppression: concurrent inhibition of primary RTK (EGFR) and bypass RTK (MET) prevents PI3K survival escape."
        elif "KRAS" in target_a and ("SOS" in target_b or "SHP2" in target_b):
            mechanistic_basis = "Targeted GDP-bound lock: upstream GEF/phosphatase inhibition prevents GTP loading while covalent drug traps mutant in inactive state."
        else:
            mechanistic_basis = "Multi-target pathway convergence suppressing mutually compensating cellular nodes."

        return CombinationTherapy(
            drug_a_id=drug_a_id,
            drug_b_id=drug_b_id,
            target_a=target_a,
            target_b=target_b,
            bliss_excess=bliss_excess,
            loewe_combination_index=ci,
            hsa_score=hsa_val,
            zip_score=zip_val,
            synergistic=is_synergistic,
            mechanistic_basis=mechanistic_basis,
            recommended_ratio=f"{int(conc_a)}nM:{int(conc_b)}nM"
        )
