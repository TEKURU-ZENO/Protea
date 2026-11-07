"""
PROTEA Phase 10: Multi-Objective Therapeutic Optimizer
Finds Pareto-optimal therapeutic protocols balancing pathway inhibition, essential preservation, and toxicity.
"""

from __future__ import annotations
from typing import List, Dict, Any
from ai.mutation_therapeutics.schema import TherapeuticScenario


class MultiObjectiveTherapeuticOptimizer:
    """Calculates Pareto dominance and discovers non-dominated therapeutic scenarios."""

    @classmethod
    def evaluate_pareto_frontier(
        cls,
        scenarios: List[TherapeuticScenario]
    ) -> List[TherapeuticScenario]:
        """
        Evaluates Pareto dominance across:
        - Inhibit Disease Pathway (Higher is better)
        - Retain Essential Genes (Higher is better)
        - Toxicity (Lower is better)
        """
        for i, s1 in enumerate(scenarios):
            is_dominated = False
            for j, s2 in enumerate(scenarios):
                if i == j:
                    continue

                # s2 dominates s1 if s2 is >= s1 in all objectives and strictly > in at least one
                better_or_equal = (
                    s2.disease_pathway_inhibition >= s1.disease_pathway_inhibition and
                    s2.essential_gene_retention >= s1.essential_gene_retention and
                    s2.toxicity_estimate <= s1.toxicity_estimate
                )
                strictly_better = (
                    s2.disease_pathway_inhibition > s1.disease_pathway_inhibition or
                    s2.essential_gene_retention > s1.essential_gene_retention or
                    s2.toxicity_estimate < s1.toxicity_estimate
                )

                if better_or_equal and strictly_better:
                    is_dominated = True
                    break

            s1.pareto_optimal = not is_dominated

        # Sort scenarios: Pareto-optimal first, then by composite objective score
        def score(s: TherapeuticScenario) -> float:
            base = (s.disease_pathway_inhibition * 0.50) + (s.essential_gene_retention * 0.30) - (s.toxicity_estimate * 0.20)
            return base + (1.0 if s.pareto_optimal else 0.0)

        scenarios.sort(key=score, reverse=True)
        return scenarios
