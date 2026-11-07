"""
PROTEA Phase 10: Allosteric Perturbation Engine
Traces propagation of conformational distortion from mutated positions to catalytic and allosteric pockets.
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional


class AllostericPerturbationEngine:
    """Detects long-range conformational coupling and catalytic site distortion."""

    @classmethod
    def trace_allosteric_coupling(
        cls,
        gene_symbol: str,
        position: int,
        backbone_rmsd: float,
        catalytic_center_residue: int = 576
    ) -> Dict[str, Any]:
        """
        Traces mechanical distortion propagation across residue contact networks.
        """
        gene = gene_symbol.upper()

        # Distance along sequence or in 3D contact network
        linear_distance = abs(position - catalytic_center_residue)

        # In kinases, activation loop (e.g., 600 in BRAF) directly contacts catalytic loop (576)
        coupling_coefficient = 1.0 / (1.0 + (linear_distance * 0.05))

        # Effective pocket displacement
        pocket_distortion_angstrom = round(backbone_rmsd * coupling_coefficient * 1.8, 2)
        pocket_disrupted = pocket_distortion_angstrom >= 0.40

        affected_pockets: List[str] = []
        if pocket_disrupted:
            affected_pockets.append("ATP-binding cleft")
            affected_pockets.append("Activation switch")
            if gene == "BRAF":
                affected_pockets.append("MEK-binding interface")
            elif gene == "EGFR":
                affected_pockets.append("Dimerization interface")

        return {
            "gene": gene,
            "mutated_position": position,
            "catalytic_center": catalytic_center_residue,
            "coupling_coefficient": round(coupling_coefficient, 2),
            "pocket_distortion_angstrom": pocket_distortion_angstrom,
            "is_catalytically_perturbed": pocket_disrupted,
            "affected_regulatory_pockets": affected_pockets
        }
