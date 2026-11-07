"""In-silico gene and reaction knockouts and essentiality analysis."""

import copy
from typing import Any, Dict, List, Tuple
from ai.cellular_simulation.schema import SimulationModel
from ai.cellular_simulation.metabolism.fba import FluxBalanceAnalysis


class MetabolicKnockoutAnalyzer:
    """Performs single and double knockout screens on metabolic models."""

    def __init__(self, model: SimulationModel):
        self.model = model
        self.base_fba = FluxBalanceAnalysis(model)

    def single_knockout_screen(
        self,
        essentiality_threshold: float = 0.05,
    ) -> Dict[str, Dict[str, Any]]:
        """Systematically knock out each reaction and measure relative growth rate impact."""
        wild_type_res = self.base_fba.optimize()
        wt_growth = wild_type_res.metrics.get("objective_value", 0.0)

        results = {}

        for rxn in self.model.reactions:
            rxn_id = rxn.reaction_id
            # Clone model
            model_ko = copy.deepcopy(self.model)
            for r in model_ko.reactions:
                if r.reaction_id == rxn_id:
                    r.parameters["lb"] = 0.0
                    r.parameters["ub"] = 0.0

            fba_ko = FluxBalanceAnalysis(model_ko)
            ko_res = fba_ko.optimize()
            ko_growth = ko_res.metrics.get("objective_value", 0.0)

            ratio = (ko_growth / wt_growth) if wt_growth > 0 else 0.0
            is_essential = bool(ratio < essentiality_threshold)

            results[rxn_id] = {
                "growth_rate": ko_growth,
                "relative_growth": ratio,
                "is_essential": is_essential,
            }

        return results
