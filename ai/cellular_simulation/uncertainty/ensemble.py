"""Ensemble trajectory simulation and confidence interval aggregation."""

import copy
import time
import uuid
from typing import Dict, List, Optional, Tuple
import numpy as np

from ai.cellular_simulation.schema import SimulationModel, SimulationResult, Trajectory
from ai.cellular_simulation.deterministic.ode_engine import ODEDynamicsEngine
from ai.cellular_simulation.uncertainty.monte_carlo import MonteCarloSampler


class EnsembleSimulator:
    """Runs simulations across parameter ensembles to compute uncertainty bands."""

    def __init__(self, model: SimulationModel):
        self.model = model

    def simulate_ensemble(
        self,
        num_runs: int = 30,
        cv: float = 0.2,
        t_span: Tuple[float, float] = (0.0, 50.0),
        dt: float = 0.5,
        seed: int = 42,
        job_id: Optional[str] = None,
    ) -> SimulationResult:
        if job_id is None:
            job_id = f"ens_{uuid.uuid4().hex[:8]}"

        base_params = {k: v.value for k, v in self.model.parameters.items()}
        sampled_params = MonteCarloSampler.sample_parameters(
            base_params,
            num_samples=num_runs,
            coefficient_of_variation=cv,
            seed=seed,
        )

        species_ids = list(self.model.species.keys())
        all_runs: Dict[str, List[List[float]]] = {s: [] for s in species_ids}
        time_points: List[float] = []

        start_time = time.time()

        for idx, p_set in enumerate(sampled_params):
            model_sample = copy.deepcopy(self.model)
            for p, v in p_set.items():
                model_sample.parameters[p].value = v
                for r in model_sample.reactions:
                    if p in r.parameters:
                        r.parameters[p] = v

            engine = ODEDynamicsEngine(model_sample)
            try:
                res = engine.simulate(t_span=t_span, dt=dt, solver="LSODA")
                if not time_points:
                    time_points = res.trajectory.times

                for s in species_ids:
                    all_runs[s].append(res.trajectory.species_trajectories[s])
            except Exception:
                continue

        elapsed = time.time() - start_time

        # Calculate mean and 95% confidence intervals
        mean_trajectories: Dict[str, List[float]] = {}
        uncertainty_intervals: Dict[str, Dict[str, List[float]]] = {}

        for s in species_ids:
            runs_matrix = np.array(all_runs[s])
            if len(runs_matrix) > 0:
                mean_trajectories[s] = [float(x) for x in np.mean(runs_matrix, axis=0)]
                lower_ci = [float(x) for x in np.percentile(runs_matrix, 2.5, axis=0)]
                upper_ci = [float(x) for x in np.percentile(runs_matrix, 97.5, axis=0)]
                uncertainty_intervals[s] = {"ci_lower": lower_ci, "ci_upper": upper_ci}
            else:
                mean_trajectories[s] = [0.0] * len(time_points)
                uncertainty_intervals[s] = {"ci_lower": [0.0] * len(time_points), "ci_upper": [0.0] * len(time_points)}

        trajectory_obj = Trajectory(
            times=time_points,
            species_trajectories=mean_trajectories,
            time_unit="second",
            concentration_unit="uM",
        )

        return SimulationResult(
            job_id=job_id,
            model_id=self.model.model_id,
            model_type=self.model.model_type,
            solver="Ensemble_Monte_Carlo",
            trajectory=trajectory_obj,
            execution_time_seconds=elapsed,
            is_steady_state=False,
            metrics={"num_ensemble_runs": num_runs, "successful_runs": len(all_runs[species_ids[0]])},
            uncertainty_intervals=uncertainty_intervals,
        )
