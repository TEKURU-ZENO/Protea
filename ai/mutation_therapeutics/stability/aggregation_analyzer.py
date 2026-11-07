"""
PROTEA Phase 10: Aggregation Analyzer
Predicts protein aggregation propensity shifts and changes in aqueous solubility upon mutation.
"""

from __future__ import annotations
from typing import Dict, Any


class AggregationAnalyzer:
    """Predicts beta-sheet aggregation nucleation and solubility variations."""

    @classmethod
    def analyze_aggregation(
        cls,
        wildtype_aa: str,
        mutant_aa: str,
        local_hydrophobic_density: float = 0.45
    ) -> Dict[str, Any]:
        """
        Estimates aggregation score shifts based on hydrophobicity, beta-branching, and charge.
        """
        wt = wildtype_aa.upper()
        mut = mutant_aa.upper()

        # Beta-branched hydrophobic residues promote amyloidogenic aggregation
        beta_branched = {"I", "V", "T"}
        hydrophobic_aromatics = {"F", "Y", "W"}
        charged = {"D", "E", "K", "R"}

        delta_score = 0.0

        if mut in hydrophobic_aromatics and wt not in hydrophobic_aromatics:
            delta_score += 0.35
        if mut in beta_branched and wt not in beta_branched:
            delta_score += 0.25

        if mut in charged and wt not in charged:
            delta_score -= 0.30  # Solubilizing
        elif wt in charged and mut not in charged:
            delta_score += 0.20  # Loss of solubilizing gatekeeper

        delta_score = round(delta_score, 2)
        increased_aggregation = delta_score > 0.15

        return {
            "aggregation_propensity_delta": delta_score,
            "increased_aggregation_risk": increased_aggregation,
            "solubility_shift": "DECREASED" if delta_score > 0 else ("INCREASED" if delta_score < 0 else "UNCHANGED"),
            "confidence": 0.84
        }
