"""
PROTEA Phase 10: Structural Confidence Evaluator
Quantifies pLDDT, Predicted Aligned Error (PAE), and confidence calibration for structural mutations.
"""

from __future__ import annotations
from typing import Dict, Any


class StructuralConfidenceEvaluator:
    """Evaluates the reliability of predicted mutant structural models."""

    @classmethod
    def evaluate_confidence(
        cls,
        plddt_score: float,
        backbone_rmsd: float,
        pae_mean_angstrom: float = 4.2
    ) -> Dict[str, Any]:
        """
        Calculates confidence tier and reliability flags.
        pLDDT >= 90: Very High confidence
        70 <= pLDDT < 90: High confidence (well-modeled backbone)
        50 <= pLDDT < 70: Low confidence
        pLDDT < 50: Very Low / Intrinsically Disordered
        """
        if plddt_score >= 90.0:
            tier = "VERY_HIGH"
            reliable = True
        elif plddt_score >= 70.0:
            tier = "HIGH"
            reliable = True
        elif plddt_score >= 50.0:
            tier = "LOW"
            reliable = False
        else:
            tier = "VERY_LOW_DISORDERED"
            reliable = False

        # Structural deformation index
        deformation_index = round((backbone_rmsd * 0.6) + (pae_mean_angstrom * 0.1), 2)

        return {
            "plddt": plddt_score,
            "pae_mean_angstrom": pae_mean_angstrom,
            "confidence_tier": tier,
            "is_structurally_reliable": reliable,
            "deformation_index": deformation_index,
            "recommendation": (
                "Structure suitable for interface mapping and binding pocket modeling."
                if reliable
                else "Caution: Region exhibits structural flexibility or high predicted error."
            )
        }
