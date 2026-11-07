"""Scenario Comparison and Delta Visualizer."""

from __future__ import annotations

from typing import Any, Dict, List
from ai.digital_twin.schema import MolecularState, ScenarioResult


class ScenarioDeltaVisualizer:
    """Computes entity-level delta shifts and pathway perturbations between baseline and scenario."""

    def compute_delta(
        self,
        baseline_states: Dict[str, MolecularState],
        scenario_result: ScenarioResult
    ) -> Dict[str, Any]:
        """Calculates differences between baseline and simulated states."""
        deltas: List[Dict[str, Any]] = []

        for entity, sim_state in scenario_result.perturbed_states.items():
            base_state = baseline_states.get(entity)
            if not base_state:
                continue

            expr_delta = round((sim_state.gene_expression or 0.0) - (base_state.gene_expression or 0.0), 2)
            abund_delta = round((sim_state.protein_abundance or 0.0) - (base_state.protein_abundance or 0.0), 2)
            act_delta = round((sim_state.protein_activity or 0.0) - (base_state.protein_activity or 0.0), 2)

            if expr_delta != 0.0 or abund_delta != 0.0 or act_delta != 0.0:
                deltas.append({
                    "entity": entity,
                    "expression_delta": expr_delta,
                    "abundance_delta": abund_delta,
                    "activity_delta": act_delta,
                    "status": sim_state.status
                })

        # Sort by absolute activity/abundance delta
        sorted_deltas = sorted(deltas, key=lambda x: abs(x["activity_delta"]) + abs(x["expression_delta"]), reverse=True)

        return {
            "scenario_id": scenario_result.scenario_id,
            "target_entities": scenario_result.target_entities,
            "intervention_type": scenario_result.intervention_type,
            "affected_entities_count": len(sorted_deltas),
            "top_perturbed_entities": sorted_deltas[:10],
            "pathway_shifts": scenario_result.pathway_shifts,
            "uncertainty_score": scenario_result.uncertainty_score
        }
