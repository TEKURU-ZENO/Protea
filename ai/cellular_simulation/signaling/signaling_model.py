"""Signaling pathway simulation and dose-response analysis."""

import uuid
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from ai.cellular_simulation.schema import SimulationModel, SimulationResult
from ai.cellular_simulation.deterministic.ode_engine import ODEDynamicsEngine
from ai.cellular_simulation.signaling.cascade import SignalingCascadeAnalyzer


class SignalingEngine:
    """Specialized engine for signaling cascades, feedback loops, and dose-response titrations."""

    def __init__(self, model: SimulationModel):
        self.model = model
        self.ode_engine = ODEDynamicsEngine(model)

    def simulate_cascade(
        self,
        t_span: Tuple[float, float] = (0.0, 60.0),
        dt: float = 0.1,
        tiers: Optional[List[str]] = None,
        job_id: Optional[str] = None,
    ) -> SimulationResult:
        """Run cascade simulation and compute propagation delay and amplification metrics."""
        result = self.ode_engine.simulate(t_span=t_span, dt=dt, solver="LSODA", job_id=job_id)
        if tiers:
            analysis = SignalingCascadeAnalyzer.calculate_amplification_and_delay(result.trajectory, tiers)
            result.metrics["cascade_tier_analysis"] = analysis
        return result

    def simulate_dose_response(
        self,
        stimulus_species: str,
        response_species: str,
        doses: List[float],
        t_end: float = 100.0,
    ) -> Dict[str, Any]:
        """Titrate stimulus concentration across orders of magnitude to measure ultrasensitivity."""
        responses = []
        original_init = self.model.species[stimulus_species].initial_amount

        for dose in doses:
            self.model.species[stimulus_species].initial_amount = dose
            res = self.ode_engine.simulate(t_span=(0.0, t_end), dt=0.5, solver="LSODA")
            final_resp = res.trajectory.species_trajectories[response_species][-1]
            responses.append(float(final_resp))

        # Restore original
        self.model.species[stimulus_species].initial_amount = original_init

        # Estimate EC50
        min_r = min(responses)
        max_r = max(responses)
        half_max = min_r + 0.5 * (max_r - min_r)
        ec50 = float(np.interp(half_max, responses, doses)) if max_r > min_r else doses[len(doses)//2]

        return {
            "stimulus_species": stimulus_species,
            "response_species": response_species,
            "doses": doses,
            "responses": responses,
            "ec50": ec50,
            "max_response": max_r,
            "basal_response": min_r,
        }
