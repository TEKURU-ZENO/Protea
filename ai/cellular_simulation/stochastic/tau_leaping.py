"""Tau-leaping approximate stochastic simulation algorithm."""

import time
import uuid
from typing import Dict, List, Optional, Tuple
import numpy as np

from ai.cellular_simulation.schema import SimulationModel, SimulationResult, Trajectory
from ai.cellular_simulation.stochastic.stochastic_network import StochasticNetwork


class TauLeapingEngine:
    """Explicit tau-leaping algorithm for fast stochastic simulation."""

    def __init__(self, model: SimulationModel):
        self.model = model
        self.network = StochasticNetwork(model)

    def simulate(
        self,
        t_span: Tuple[float, float] = (0.0, 50.0),
        tau: float = 0.1,
        random_seed: Optional[int] = None,
        job_id: Optional[str] = None,
    ) -> SimulationResult:
        if job_id is None:
            job_id = f"tau_{uuid.uuid4().hex[:8]}"

        rng = np.random.RandomState(random_seed)
        t_start, t_end = t_span

        species_ids = self.network.species_ids
        curr_state = np.array(
            [int(round(self.model.species[s].initial_amount)) for s in species_ids],
            dtype=np.int64,
        )

        times = [t_start]
        states = [np.copy(curr_state)]

        t = t_start
        start_wall_time = time.time()

        while t < t_end:
            step_tau = min(tau, t_end - t)
            propensities = self.network.compute_propensities(curr_state)

            # Poisson draws for each reaction
            firings = np.zeros(len(propensities), dtype=np.int64)
            for j in range(len(propensities)):
                rate = propensities[j] * step_tau
                if rate > 0:
                    firings[j] = rng.poisson(rate)

            # Proposed state change
            delta = self.network.S_matrix.dot(firings).astype(np.int64)
            next_state = curr_state + delta

            # Check if any species became negative
            if np.any(next_state < 0):
                # Step was too large; halve tau and retry
                step_tau *= 0.5
                continue

            # Update constant vs non-constant species
            for idx, s_id in enumerate(species_ids):
                if not self.model.species[s_id].is_constant:
                    curr_state[idx] = max(0, next_state[idx])

            t += step_tau
            times.append(t)
            states.append(np.copy(curr_state))

        elapsed = time.time() - start_wall_time
        states_arr = np.array(states)

        trajectories: Dict[str, List[float]] = {}
        for idx, s_id in enumerate(species_ids):
            trajectories[s_id] = [float(val) for val in states_arr[:, idx]]

        trajectory_obj = Trajectory(
            times=[float(x) for x in times],
            species_trajectories=trajectories,
            time_unit="second",
            concentration_unit="molecules",
        )

        return SimulationResult(
            job_id=job_id,
            model_id=self.model.model_id,
            model_type="STOCHASTIC",
            solver="Tau_Leaping",
            trajectory=trajectory_obj,
            execution_time_seconds=elapsed,
            is_steady_state=False,
            metrics={"time_steps": len(times), "final_time": float(t)},
        )
