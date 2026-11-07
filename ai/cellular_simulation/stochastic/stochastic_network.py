"""Stochastic network representations and propensity functions."""

from typing import Dict, List, Tuple
import numpy as np
from ai.cellular_simulation.schema import SimulationModel
from ai.cellular_simulation.model_builder.stoichiometry import StoichiometryBuilder


class StochasticNetwork:
    """Computes discrete molecule reaction propensities a_j(X) and updates discrete states."""

    def __init__(self, model: SimulationModel, volume_liters: float = 1e-15):
        self.model = model
        self.species_ids = list(model.species.keys())
        self.species_indices = {s_id: idx for idx, s_id in enumerate(self.species_ids)}
        self.S_matrix, _, self.reaction_ids = StoichiometryBuilder.build_matrix(model)
        self.volume_liters = volume_liters

    def compute_propensities(self, state: np.ndarray) -> np.ndarray:
        """Compute reaction propensity vector a(X) for discrete molecule counts."""
        propensities = np.zeros(len(self.model.reactions), dtype=float)

        for idx, rxn in enumerate(self.model.reactions):
            rate_law = rxn.rate_law_type
            params = rxn.parameters
            k = params.get("k_f", params.get("kcat", params.get("Vmax", 0.1)))

            # If no reactants (zeroth-order synthesis)
            if not rxn.reactants:
                propensities[idx] = float(k)
                continue

            # Compute combinatorial terms for reactants
            comb = 1.0
            possible = True
            for r_id, coeff in rxn.reactants.items():
                s_idx = self.species_indices[r_id]
                count = int(state[s_idx])
                stk = int(coeff)
                if count < stk:
                    possible = False
                    comb = 0.0
                    break
                if stk == 1:
                    comb *= count
                elif stk == 2:
                    comb *= (count * (count - 1)) / 2.0
                else:
                    # Generic factorial product
                    prod = 1.0
                    for c in range(stk):
                        prod *= (count - c)
                    comb *= prod

            if not possible:
                propensities[idx] = 0.0
            else:
                propensities[idx] = max(0.0, float(k * comb))

        return propensities
