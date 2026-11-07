"""Metabolic medium conditions and uptake constraint configuration."""

from typing import Dict, Optional
from ai.cellular_simulation.schema import SimulationModel


class MetabolicConstraintsManager:
    """Manages environmental nutrient uptake constraints and boundary bounds."""

    @staticmethod
    def apply_uptake_bounds(
        model: SimulationModel,
        uptake_bounds: Dict[str, float], # reaction_id -> max uptake rate (positive number)
    ) -> None:
        """Set upper bounds for nutrient uptake reactions."""
        for rxn in model.reactions:
            if rxn.reaction_id in uptake_bounds:
                max_rate = uptake_bounds[rxn.reaction_id]
                rxn.parameters["ub"] = float(max_rate)
                # Ensure non-negative lower bound for irreversible uptake
                if "lb" not in rxn.parameters:
                    rxn.parameters["lb"] = 0.0

    @staticmethod
    def set_aerobic_condition(model: SimulationModel, is_aerobic: bool = True) -> None:
        """Switch between aerobic and anaerobic condition by altering oxygen uptake."""
        for rxn in model.reactions:
            if "oxygen" in rxn.reaction_id.lower() or "o2" in rxn.reaction_id.lower():
                rxn.parameters["ub"] = 20.0 if is_aerobic else 0.0
