"""Local sensitivity analysis via finite differences."""

import copy
from typing import Dict, List, Tuple
import numpy as np

from ai.cellular_simulation.schema import SimulationModel
from ai.cellular_simulation.deterministic.ode_engine import ODEDynamicsEngine


class LocalSensitivityAnalyzer:
    """Computes normalized local sensitivity coefficients S_ij = (dy_i / dtheta_j) * (theta_j / y_i)."""

    def __init__(self, model: SimulationModel):
        self.model = model
        self.engine = ODEDynamicsEngine(model)

    def analyze(
        self,
        parameters_to_test: List[str],
        observables: List[str],
        t_span: Tuple[float, float] = (0.0, 50.0),
        perturbation_fraction: float = 0.01,
    ) -> Dict[str, Dict[str, float]]:
        """Calculate normalized sensitivity of final observable concentrations to parameters."""
        # Baseline simulation
        base_res = self.engine.simulate(t_span=t_span, dt=0.5, solver="LSODA")
        base_vals = {
            obs: base_res.trajectory.species_trajectories[obs][-1]
            for obs in observables
            if obs in base_res.trajectory.species_trajectories
        }

        sensitivities: Dict[str, Dict[str, float]] = {obs: {} for obs in base_vals.keys()}

        for p_name in parameters_to_test:
            if p_name not in self.model.parameters:
                continue

            base_p = self.model.parameters[p_name].value
            delta_p = perturbation_fraction * max(1e-6, base_p)

            # Up perturbation
            model_up = copy.deepcopy(self.model)
            model_up.parameters[p_name].value = base_p + delta_p
            for r in model_up.reactions:
                if p_name in r.parameters:
                    r.parameters[p_name] = base_p + delta_p
            res_up = ODEDynamicsEngine(model_up).simulate(t_span=t_span, dt=0.5, solver="LSODA")

            # Down perturbation
            model_down = copy.deepcopy(self.model)
            model_down.parameters[p_name].value = max(1e-9, base_p - delta_p)
            for r in model_down.reactions:
                if p_name in r.parameters:
                    r.parameters[p_name] = max(1e-9, base_p - delta_p)
            res_down = ODEDynamicsEngine(model_down).simulate(t_span=t_span, dt=0.5, solver="LSODA")

            for obs in base_vals.keys():
                y_base = base_vals[obs]
                y_up = res_up.trajectory.species_trajectories[obs][-1]
                y_down = res_down.trajectory.species_trajectories[obs][-1]

                dy = y_up - y_down
                dp = 2.0 * delta_p

                if abs(y_base) > 1e-9 and dp > 0:
                    norm_sens = (dy / dp) * (base_p / y_base)
                else:
                    norm_sens = 0.0

                sensitivities[obs][p_name] = float(norm_sens)

        return sensitivities
