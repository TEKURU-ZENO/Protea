"""Reproducibility verification across simulation runs."""

from typing import Any, Dict, List
import numpy as np

from ai.cellular_simulation.model_builder.model_factory import ModelFactory
from ai.cellular_simulation.stochastic.gillespie import GillespieEngine


class ReproducibilityVerifier:
    """Verifies deterministic repeatability of simulations under identical seeds."""

    @staticmethod
    def verify_seed_repeatability(seed: int = 12345) -> Dict[str, Any]:
        model = ModelFactory.create_goldbeter_koshland_model()
        engine = GillespieEngine(model)

        run1 = engine.simulate(t_span=(0.0, 20.0), dt_record=0.5, random_seed=seed)
        run2 = engine.simulate(t_span=(0.0, 20.0), dt_record=0.5, random_seed=seed)

        traj1 = run1.trajectory.species_trajectories
        traj2 = run2.trajectory.species_trajectories

        exact_match = True
        max_diff = 0.0

        for s_id in traj1.keys():
            diff = np.max(np.abs(np.array(traj1[s_id]) - np.array(traj2[s_id])))
            if diff > 1e-9:
                exact_match = False
                max_diff = max(max_diff, float(diff))

        return {
            "seed": seed,
            "exact_match": exact_match,
            "max_difference": max_diff,
            "status": "PASS" if exact_match else "FAIL",
        }
