"""Flux Variability Analysis (FVA) for determining allowable flux ranges."""

from typing import Dict, List, Optional, Tuple
import numpy as np
from scipy.optimize import linprog

from ai.cellular_simulation.schema import SimulationModel
from ai.cellular_simulation.metabolism.fba import FluxBalanceAnalysis


class FluxVariabilityAnalysis:
    """Calculates min and max achievable flux for each reaction given an optimal objective fraction."""

    def __init__(self, model: SimulationModel):
        self.model = model
        self.fba = FluxBalanceAnalysis(model)

    def analyze(
        self,
        fraction_of_optimum: float = 0.95,
        objective_reaction: Optional[str] = None,
    ) -> Dict[str, Tuple[float, float]]:
        """Compute [min_flux, max_flux] for each reaction at >= fraction_of_optimum * Z*."""
        # 1. Run base FBA to find optimal objective Z*
        base_fba = self.fba.optimize(objective_reaction=objective_reaction)
        z_opt = base_fba.metrics.get("objective_value", 0.0)
        target_z = fraction_of_optimum * z_opt

        n_rxns = len(self.fba.reaction_ids)

        # Objective vector c
        c_vec = np.zeros(n_rxns, dtype=float)
        if objective_reaction is None:
            for idx, rxn in enumerate(self.model.reactions):
                if rxn.parameters.get("objective_weight", 0.0) > 0:
                    c_vec[idx] = rxn.parameters["objective_weight"]
            if np.all(c_vec == 0) and n_rxns > 0:
                c_vec[-1] = 1.0
        else:
            c_vec[self.fba.reaction_ids.index(objective_reaction)] = 1.0

        # Base bounds
        bounds = []
        for rxn in self.model.reactions:
            lb = rxn.parameters.get("lb", 0.0 if not rxn.reversible else -1000.0)
            ub = rxn.parameters.get("ub", 1000.0)
            bounds.append((lb, ub))

        # Inequality constraint: c^T v >= target_z  =>  -c^T v <= -target_z
        A_ub = -c_vec.reshape(1, -1)
        b_ub = np.array([-target_z])

        # Internal species for steady-state equality constraints
        internal_indices = [
            i for i, s_id in enumerate(self.fba.species_ids)
            if not self.model.species[s_id].is_constant
        ]
        if internal_indices:
            A_eq = self.fba.S_matrix[internal_indices, :]
            b_eq = np.zeros(len(internal_indices))
        else:
            A_eq = self.fba.S_matrix
            b_eq = np.zeros(len(self.fba.species_ids))

        flux_ranges: Dict[str, Tuple[float, float]] = {}

        for i, rxn_id in enumerate(self.fba.reaction_ids):
            # Target vector for reaction i
            target_vec = np.zeros(n_rxns, dtype=float)
            target_vec[i] = 1.0

            # Minimize v_i: min c^T v
            res_min = linprog(
                c=target_vec,
                A_ub=A_ub,
                b_ub=b_ub,
                A_eq=A_eq,
                b_eq=b_eq,
                bounds=bounds,
                method="highs",
            )
            min_val = float(res_min.fun) if res_min.success else bounds[i][0]

            # Maximize v_i: min -c^T v
            res_max = linprog(
                c=-target_vec,
                A_ub=A_ub,
                b_ub=b_ub,
                A_eq=A_eq,
                b_eq=b_eq,
                bounds=bounds,
                method="highs",
            )
            max_val = -float(res_max.fun) if res_max.success else bounds[i][1]

            flux_ranges[rxn_id] = (min_val, max_val)

        return flux_ranges
