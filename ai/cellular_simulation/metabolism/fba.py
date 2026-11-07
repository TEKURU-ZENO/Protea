"""Flux Balance Analysis (FBA) using Linear Programming."""

import time
import uuid
from typing import Dict, List, Optional, Tuple
import numpy as np
from scipy.optimize import linprog

from ai.cellular_simulation.schema import SimulationModel, SimulationResult, Trajectory
from ai.cellular_simulation.model_builder.stoichiometry import StoichiometryBuilder


class FluxBalanceAnalysis:
    """Solves steady-state metabolic flux distribution: max c^T v subject to S*v=0 and lb <= v <= ub."""

    def __init__(self, model: SimulationModel):
        self.model = model
        self.S_matrix, self.species_ids, self.reaction_ids = StoichiometryBuilder.build_matrix(model)

    def optimize(
        self,
        objective_reaction: Optional[str] = None,
        job_id: Optional[str] = None,
    ) -> SimulationResult:
        """Run FBA optimization using HiGHS linear programming solver."""
        if job_id is None:
            job_id = f"fba_{uuid.uuid4().hex[:8]}"

        n_rxns = len(self.reaction_ids)
        c_vec = np.zeros(n_rxns, dtype=float)

        # Identify objective reaction
        if objective_reaction is None:
            # Check metadata or reaction parameters
            for idx, rxn in enumerate(self.model.reactions):
                if rxn.parameters.get("objective_weight", 0.0) > 0:
                    c_vec[idx] = rxn.parameters["objective_weight"]
            if np.all(c_vec == 0) and n_rxns > 0:
                # Default to last reaction (usually biomass)
                c_vec[-1] = 1.0
        else:
            if objective_reaction in self.reaction_ids:
                idx = self.reaction_ids.index(objective_reaction)
                c_vec[idx] = 1.0
            else:
                raise ValueError(f"Objective reaction '{objective_reaction}' not in model reactions.")

        # Extract bounds [lb, ub]
        bounds = []
        for rxn in self.model.reactions:
            lb = rxn.parameters.get("lb", 0.0 if not rxn.reversible else -1000.0)
            ub = rxn.parameters.get("ub", 1000.0)
            bounds.append((lb, ub))

        # Filter out boundary / constant species from steady-state conservation constraints
        internal_indices = [
            i for i, s_id in enumerate(self.species_ids)
            if not self.model.species[s_id].is_constant
        ]
        if internal_indices:
            A_eq = self.S_matrix[internal_indices, :]
            b_eq = np.zeros(len(internal_indices))
        else:
            A_eq = self.S_matrix
            b_eq = np.zeros(len(self.species_ids))

        # Solve LP: min -c^T v  s.t. S_internal * v = 0
        start_time = time.time()
        res = linprog(
            c=-c_vec,
            A_eq=A_eq,
            b_eq=b_eq,
            bounds=bounds,
            method="highs",
        )
        elapsed = time.time() - start_time

        if not res.success:
            flux_dict = {rxn_id: 0.0 for rxn_id in self.reaction_ids}
            obj_val = 0.0
        else:
            flux_dict = {rxn_id: float(val) for rxn_id, val in zip(self.reaction_ids, res.x)}
            obj_val = -float(res.fun)

        # For FBA, create single-point trajectory
        trajectory = Trajectory(
            times=[0.0],
            species_trajectories={s: [self.model.species[s].initial_amount] for s in self.species_ids},
            time_unit="steady_state",
            concentration_unit="mmol/gDW",
        )

        return SimulationResult(
            job_id=job_id,
            model_id=self.model.model_id,
            model_type="METABOLIC",
            solver="HiGHS_LP",
            trajectory=trajectory,
            fluxes=flux_dict,
            execution_time_seconds=elapsed,
            is_steady_state=True,
            metrics={
                "objective_value": obj_val,
                "solver_status": res.message,
                "success": bool(res.success),
            },
        )
