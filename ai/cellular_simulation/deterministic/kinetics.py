"""Kinetics evaluator for deterministic ODE reaction networks."""

from typing import Dict, List, Tuple
import numpy as np
from ai.cellular_simulation.schema import SimulationModel
from ai.cellular_simulation.model_builder.reaction_parser import ReactionRateEvaluator
from ai.cellular_simulation.model_builder.stoichiometry import StoichiometryBuilder


class KineticsEvaluator:
    """Evaluates reaction flux vectors and species time derivatives dx/dt = S * v."""

    def __init__(self, model: SimulationModel):
        self.model = model
        self.species_ids = list(model.species.keys())
        self.species_indices = {s_id: idx for idx, s_id in enumerate(self.species_ids)}
        self.S_matrix, _, self.reaction_ids = StoichiometryBuilder.build_matrix(model)

    def compute_fluxes(self, state_dict: Dict[str, float]) -> np.ndarray:
        """Calculate reaction velocity vector v(t) given current molecular species state."""
        fluxes = np.zeros(len(self.model.reactions), dtype=float)
        for idx, rxn in enumerate(self.model.reactions):
            fluxes[idx] = ReactionRateEvaluator.evaluate_rate(rxn, state_dict)
        return fluxes

    def derivatives(self, t: float, y: np.ndarray) -> np.ndarray:
        """Calculate state derivatives dy/dt = S * v for ODE solvers."""
        # Map y array to species dict
        state_dict: Dict[str, float] = {}
        for idx, s_id in enumerate(self.species_ids):
            val = float(y[idx])
            # Prevent non-physical negative concentrations in rate evaluation
            state_dict[s_id] = max(0.0, val)

        fluxes = self.compute_fluxes(state_dict)

        # dydt = S * v
        if self.S_matrix.shape[1] == len(fluxes):
            dydt = self.S_matrix.dot(fluxes)
        else:
            dydt = np.zeros(len(self.species_ids), dtype=float)

        # Boundary / constant species have zero time derivative
        for idx, s_id in enumerate(self.species_ids):
            if self.model.species[s_id].is_constant:
                dydt[idx] = 0.0

        return dydt
