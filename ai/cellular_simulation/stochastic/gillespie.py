"""Gillespie Stochastic Simulation Algorithm (SSA) and First Reaction Method."""

import time
import uuid
from typing import Dict, List, Optional, Tuple
import numpy as np

from ai.cellular_simulation.schema import SimulationModel, SimulationResult, Trajectory
from ai.cellular_simulation.stochastic.stochastic_network import StochasticNetwork


class GillespieEngine:
    """Exact Stochastic Simulation Algorithm (SSA) for discrete molecular reaction systems."""

    def __init__(self, model: SimulationModel):
        self.model = model
        self.network = StochasticNetwork(model)

    def simulate(
        self,
        t_span: Tuple[float, float] = (0.0, 50.0),
        dt_record: float = 0.5,
        max_steps: int = 200000,
        random_seed: Optional[int] = None,
        job_id: Optional[str] = None,
    ) -> SimulationResult:
        """Run Gillespie SSA exact stochastic simulation."""
        if job_id is None:
            job_id = f"ssa_{uuid.uuid4().hex[:8]}"

        rng = np.random.RandomState(random_seed)
        t_start, t_end = t_span

        species_ids = self.network.species_ids
        initial_counts = np.array(
            [int(round(self.model.species[s].initial_amount)) for s in species_ids],
            dtype=np.int64,
        )

        curr_state = np.copy(initial_counts)
        curr_t = float(t_start)

        # Recording setup
        record_times = np.arange(t_start, t_end + dt_record, dt_record)
        recorded_states = np.zeros((len(record_times), len(species_ids)), dtype=np.int64)
        recorded_states[0] = curr_state

        rec_idx = 1
        steps = 0
        start_wall_time = time.time()

        while curr_t < t_end and steps < max_steps:
            steps += 1
            propensities = self.network.compute_propensities(curr_state)
            a0 = float(np.sum(propensities))

            if a0 <= 1e-12:
                # No more reactions can fire
                while rec_idx < len(record_times):
                    recorded_states[rec_idx] = curr_state
                    rec_idx += 1
                break

            # 1. Sample tau ~ Exp(a0)
            r1 = rng.uniform(1e-12, 1.0)
            tau = -np.log(r1) / a0

            # Fill recorded states up to curr_t + tau
            next_t = curr_t + tau
            while rec_idx < len(record_times) and record_times[rec_idx] <= next_t:
                recorded_states[rec_idx] = curr_state
                rec_idx += 1

            # 2. Sample reaction index mu
            r2 = rng.uniform(0.0, 1.0)
            cum_prop = np.cumsum(propensities)
            mu = int(np.searchsorted(cum_prop, r2 * a0))
            if mu >= len(propensities):
                mu = len(propensities) - 1

            # 3. Apply state change delta = S[:, mu]
            delta = self.network.S_matrix[:, mu].astype(np.int64)
            # Only update non-constant species
            for idx, s_id in enumerate(species_ids):
                if not self.model.species[s_id].is_constant:
                    curr_state[idx] = max(0, curr_state[idx] + delta[idx])

            curr_t = next_t

        # If loop exited before filling all record times
        while rec_idx < len(record_times):
            recorded_states[rec_idx] = curr_state
            rec_idx += 1

        elapsed = time.time() - start_wall_time

        trajectories: Dict[str, List[float]] = {}
        for idx, s_id in enumerate(species_ids):
            trajectories[s_id] = [float(val) for val in recorded_states[:, idx]]

        trajectory_obj = Trajectory(
            times=[float(t) for t in record_times],
            species_trajectories=trajectories,
            time_unit="second",
            concentration_unit="molecules",
        )

        return SimulationResult(
            job_id=job_id,
            model_id=self.model.model_id,
            model_type="STOCHASTIC",
            solver="Gillespie_SSA",
            trajectory=trajectory_obj,
            execution_time_seconds=elapsed,
            is_steady_state=False,
            metrics={
                "total_stochastic_steps": steps,
                "recorded_points": len(record_times),
                "terminal_time": float(curr_t),
            },
        )
