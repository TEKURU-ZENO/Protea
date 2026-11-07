"""Multiscale hybrid simulation orchestrator."""

import time
import uuid
from typing import Dict, List, Optional, Tuple
import numpy as np

from ai.cellular_simulation.schema import SimulationModel, SimulationResult, Trajectory
from ai.cellular_simulation.deterministic.ode_engine import ODEDynamicsEngine
from ai.cellular_simulation.hybrid.time_synchronization import MultiscaleClock
from ai.cellular_simulation.hybrid.model_coupling import ModelCouplingLink


class MultiscaleHybridOrchestrator:
    """Coordinates coupled simulations across multiple scales and models."""

    def __init__(
        self,
        primary_model: SimulationModel,
        clock: Optional[MultiscaleClock] = None,
        coupling_links: Optional[List[ModelCouplingLink]] = None,
    ):
        self.primary_model = primary_model
        self.clock = clock or MultiscaleClock()
        self.coupling_links = coupling_links or []
        self.ode_engine = ODEDynamicsEngine(primary_model)

    def simulate(
        self,
        job_id: Optional[str] = None,
    ) -> SimulationResult:
        """Run synchronized multiscale simulation."""
        if job_id is None:
            job_id = f"hybrid_{uuid.uuid4().hex[:8]}"

        start_wall_time = time.time()
        windows = self.clock.get_sync_windows()

        all_times: List[float] = [self.clock.t_start]
        all_species = list(self.primary_model.species.keys())
        trajectories: Dict[str, List[float]] = {
            s: [self.primary_model.species[s].initial_amount] for s in all_species
        }

        curr_state = {s: self.primary_model.species[s].initial_amount for s in all_species}

        for (w_start, w_end) in windows:
            # Set initial conditions for current window
            for s in all_species:
                self.primary_model.species[s].initial_amount = curr_state[s]

            # Simulate current window
            res = self.ode_engine.simulate(
                t_span=(w_start, w_end),
                dt=self.clock.fast_dt,
                solver="LSODA",
            )

            # Append trajectory steps (skipping first duplicate point)
            sub_times = res.trajectory.times[1:]
            all_times.extend(sub_times)
            for s in all_species:
                trajectories[s].extend(res.trajectory.species_trajectories[s][1:])
                curr_state[s] = res.trajectory.species_trajectories[s][-1]

            # Apply coupling links if any
            for link in self.coupling_links:
                if link.source_variable in curr_state:
                    source_val = curr_state[link.source_variable]
                    transformed_val = link.transfer(source_val)
                    if link.target_variable in self.primary_model.parameters:
                        self.primary_model.parameters[link.target_variable].value = transformed_val

        elapsed = time.time() - start_wall_time

        traj_obj = Trajectory(
            times=all_times,
            species_trajectories=trajectories,
            time_unit="second",
            concentration_unit="uM",
        )

        return SimulationResult(
            job_id=job_id,
            model_id=self.primary_model.model_id,
            model_type="HYBRID",
            solver="Multiscale_Hybrid_RK",
            trajectory=traj_obj,
            execution_time_seconds=elapsed,
            is_steady_state=False,
            metrics={"sync_windows": len(windows), "total_steps": len(all_times)},
        )
