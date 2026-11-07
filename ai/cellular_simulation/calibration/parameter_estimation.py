"""Parameter estimation and fitting against experimental measurements."""

import copy
import time
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from scipy.optimize import minimize

from ai.cellular_simulation.schema import SimulationModel, ParameterProvenance
from ai.cellular_simulation.deterministic.ode_engine import ODEDynamicsEngine
from ai.cellular_simulation.calibration.likelihood import CalibrationLikelihood


class ParameterEstimator:
    """Calibrates kinetic parameters of a SimulationModel using numerical optimization."""

    def __init__(self, model: SimulationModel):
        self.model = model

    def fit(
        self,
        experimental_data: Dict[str, List[float]], # species_id -> values
        experimental_times: List[float],
        parameters_to_fit: List[str],
        initial_guess: Optional[Dict[str, float]] = None,
        method: str = "Nelder-Mead",
        maxiter: int = 200,
    ) -> Dict[str, Any]:
        """Fit parameters to minimize discrepancy against experimental time-series."""
        # Baseline parameter values
        if initial_guess is None:
            initial_guess = {p: self.model.parameters[p].value for p in parameters_to_fit}

        p0 = [initial_guess[p] for p in parameters_to_fit]
        t_span = (experimental_times[0], experimental_times[-1])
        dt = (experimental_times[1] - experimental_times[0]) if len(experimental_times) > 1 else 0.5

        def objective(p_vec: np.ndarray) -> float:
            # Map p_vec back to model
            test_model = copy.deepcopy(self.model)
            for idx, p_name in enumerate(parameters_to_fit):
                val = max(1e-6, float(p_vec[idx]))
                test_model.parameters[p_name].value = val
                # Update reactions referencing this parameter
                for r in test_model.reactions:
                    if p_name in r.parameters:
                        r.parameters[p_name] = val
                    elif p_name.startswith("k_") and "k_f" in r.parameters and p_name in r.reaction_id:
                        r.parameters["k_f"] = val

            engine = ODEDynamicsEngine(test_model)
            try:
                res = engine.simulate(t_span=t_span, dt=dt, solver="LSODA")
                # Interpolate or match time points
                sim_traj = {}
                for s_id in experimental_data.keys():
                    if s_id in res.trajectory.species_trajectories:
                        sim_series = res.trajectory.species_trajectories[s_id]
                        # Interpolate to experimental_times
                        interp_vals = np.interp(
                            experimental_times,
                            res.trajectory.times,
                            sim_series,
                        )
                        sim_traj[s_id] = list(interp_vals)

                return CalibrationLikelihood.sum_of_squared_errors(sim_traj, experimental_data)
            except Exception:
                return 1e9

        start_time = time.time()
        opt_res = minimize(
            objective,
            p0,
            method=method,
            options={"maxiter": maxiter, "disp": False},
        )
        elapsed = time.time() - start_time

        fitted_params = {}
        for idx, p_name in enumerate(parameters_to_fit):
            val = float(opt_res.x[idx])
            fitted_params[p_name] = val
            # Update in self.model
            if p_name in self.model.parameters:
                self.model.parameters[p_name].value = val
                self.model.parameters[p_name].provenance = ParameterProvenance.CALIBRATED.value

        return {
            "fitted_parameters": fitted_params,
            "final_sse": float(opt_res.fun),
            "converged": bool(opt_res.success),
            "iterations": int(opt_res.nit) if hasattr(opt_res, "nit") else maxiter,
            "calibration_time_seconds": elapsed,
        }
