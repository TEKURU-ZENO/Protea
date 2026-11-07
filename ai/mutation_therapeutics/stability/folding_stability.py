"""
PROTEA Phase 10: Folding Stability Predictor
Predicts thermodynamic folding free energy changes (DeltaDeltaG in kcal/mol) and classifies destabilization.
"""

from __future__ import annotations
from typing import Dict, Any
from ai.mutation_therapeutics.schema import StabilityClass

# Physico-chemical amino acid properties
HYDROPHOBICITY_SCALE = {
    "I": 4.5, "V": 4.2, "L": 3.8, "F": 2.8, "C": 2.5, "M": 1.9, "A": 1.8,
    "G": -0.4, "T": -0.7, "S": -0.8, "W": -0.9, "Y": -1.3, "P": -1.6,
    "H": -3.2, "E": -3.5, "Q": -3.5, "D": -3.5, "N": -3.5, "K": -3.9, "R": -4.5
}


class FoldingStabilityPredictor:
    """Estimates thermodynamic folding free energy changes upon mutation."""

    @classmethod
    def predict_ddg(
        cls,
        wildtype_aa: str,
        mutant_aa: str,
        burial_fraction: float = 0.6,
        is_proline_or_glycine: bool = False
    ) -> Dict[str, Any]:
        """
        Calculates DeltaDeltaG = DeltaG(mut) - DeltaG(wt) in kcal/mol.
        DeltaDeltaG > 0 = Destabilizing.
        DeltaDeltaG < 0 = Stabilizing.
        """
        wt = wildtype_aa.upper()
        mut = mutant_aa.upper()

        if wt == mut:
            return {
                "ddg_kcal_mol": 0.0,
                "stability_class": StabilityClass.NEUTRAL,
                "confidence": 0.99
            }

        # Hydrophobicity change
        wt_hydro = HYDROPHOBICITY_SCALE.get(wt, 0.0)
        mut_hydro = HYDROPHOBICITY_SCALE.get(mut, 0.0)
        hydro_diff = wt_hydro - mut_hydro

        # Buried hydrophobic residue mutated to charged/polar creates large destabilization
        base_ddg = 0.5
        if burial_fraction > 0.5:
            base_ddg += max(0.0, hydro_diff * 0.8)

        # Proline introduces backbone rigidity/strain; Glycine adds conformational entropy
        if wt == "P" or mut == "P" or wt == "G" or mut == "G":
            base_ddg += 0.8

        # Charge creation or destruction in core
        if burial_fraction > 0.4 and mut in ["D", "E", "K", "R"]:
            base_ddg += 1.2

        ddg_val = round(base_ddg, 2)

        if ddg_val >= 3.0:
            s_class = StabilityClass.SEVERELY_DESTABILIZING
        elif ddg_val >= 1.2:
            s_class = StabilityClass.DESTABILIZING
        elif ddg_val <= -0.8:
            s_class = StabilityClass.STABILIZING
        else:
            s_class = StabilityClass.NEUTRAL

        return {
            "ddg_kcal_mol": ddg_val,
            "stability_class": s_class,
            "burial_fraction": burial_fraction,
            "confidence": 0.86
        }
