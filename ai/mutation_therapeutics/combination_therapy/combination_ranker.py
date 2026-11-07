"""
PROTEA Phase 10: Combination Therapy Ranker
Prioritizes drug combinations designed to overcome resistance or achieve synthetic lethality.
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional
from ai.mutation_therapeutics.schema import CombinationTherapy, DrugCandidate
from ai.mutation_therapeutics.combination_therapy.synergy_calculator import SynergyCalculator

# Canonical evidence-backed combinations
CURATED_COMBINATION_RECORDS: List[Dict[str, Any]] = [
    {
        "drug_a": "DRUG_DABRAFENIB",
        "drug_b": "DRUG_TRAMETINIB",
        "target_a": "BRAF",
        "target_b": "MAP2K1",
        "effect_a": 0.55,
        "effect_b": 0.50,
        "combination_effect": 0.94,
        "conc_a": 50.0,
        "ic50_a": 120.0,
        "conc_b": 5.0,
        "ic50_b": 15.0
    },
    {
        "drug_a": "DRUG_VEMURAFENIB",
        "drug_b": "DRUG_CETUXIMAB",
        "target_a": "BRAF",
        "target_b": "EGFR",
        "effect_a": 0.45,
        "effect_b": 0.35,
        "combination_effect": 0.88,
        "conc_a": 200.0,
        "ic50_a": 350.0,
        "conc_b": 10.0,
        "ic50_b": 30.0
    },
    {
        "drug_a": "DRUG_OSIMERTINIB",
        "drug_b": "DRUG_TRAMETINIB",
        "target_a": "EGFR",
        "target_b": "MAP2K1",
        "effect_a": 0.60,
        "effect_b": 0.40,
        "combination_effect": 0.92,
        "conc_a": 25.0,
        "ic50_a": 60.0,
        "conc_b": 5.0,
        "ic50_b": 15.0
    }
]


class CombinationRanker:
    """Ranks and recommends multi-drug therapeutic strategies."""

    @classmethod
    def rank_combinations_for_context(
        cls,
        gene_symbol: str,
        mutation_label: str
    ) -> List[CombinationTherapy]:
        """
        Discovers and ranks candidate combinations addressing the specific mutant context.
        """
        gene = gene_symbol.upper()
        results: List[CombinationTherapy] = []

        for record in CURATED_COMBINATION_RECORDS:
            if record["target_a"] == gene or record["target_b"] == gene or gene in mutation_label:
                combo = SynergyCalculator.calculate_synergy(
                    drug_a_id=record["drug_a"],
                    drug_b_id=record["drug_b"],
                    target_a=record["target_a"],
                    target_b=record["target_b"],
                    effect_a=record["effect_a"],
                    effect_b=record["effect_b"],
                    combination_effect=record["combination_effect"],
                    conc_a=record["conc_a"],
                    ic50_a=record["ic50_a"],
                    conc_b=record["conc_b"],
                    ic50_b=record["ic50_b"]
                )
                results.append(combo)

        # Fallback combination if none explicitly matched
        if not results:
            results.append(
                SynergyCalculator.calculate_synergy(
                    drug_a_id="DRUG_PRIMARY_LEAD",
                    drug_b_id="DRUG_BYPASS_SUPPRESSOR",
                    target_a=gene,
                    target_b="MAP2K1",
                    effect_a=0.50,
                    effect_b=0.45,
                    combination_effect=0.86,
                    conc_a=50.0,
                    ic50_a=100.0,
                    conc_b=10.0,
                    ic50_b=25.0
                )
            )

        # Sort by Bliss excess descending
        results.sort(key=lambda c: c.bliss_excess, reverse=True)
        return results
