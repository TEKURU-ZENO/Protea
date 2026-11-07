"""Deterministic Ordinary Differential Equation (ODE) Simulation Engine."""

import time
import uuid
from typing import Dict, List, Optional, Tuple
import numpy as np
from scipy.integrate import solve_ivp

from ai.cellular_simulation.schema import SimulationModel, SimulationResult, Trajectory
from ai.cellular_simulation.deterministic.kinetics import KineticsEvaluator
from ai.cellular_simulation.deterministic.rk4 import RK4Integrator
from ai.cellular_simulation.deterministic.adaptive_solver import AdaptiveRKSolver


class ODEDynamicsEngine:
    """Simulates deterministic biochemical kinetics using ODE solvers."""

    def __init__(self, model: SimulationModel):
        self.model = model
        self.evaluator = KineticsEvaluator(model)

    def simulate(
        self,
        t_span: Tuple[float, float] = (0.0, 60.0),
        dt: float = 0.1,
        solver: str = "LSODA",
        rtol: float = 1e-6,
        atol: float = 1e-9,
        job_id: Optional[str] = None,
    ) -> SimulationResult:
        """Run deterministic ODE simulation.
        
        Args:
            t_span: (t_start, t_end) in seconds
            dt: evaluation / output resolution step size
            solver: 'LSODA', 'RK45', 'BDF', 'RK4', or 'RKF45'
            rtol: relative tolerance for adaptive solvers
            atol: absolute tolerance for adaptive solvers
            job_id: optional tracking ID
        """
        if job_id is None:
            job_id = f"sim_{uuid.uuid4().hex[:8]}"

        species_ids = list(self.model.species.keys())
        y0 = np.array([self.model.species[s].initial_amount for s in species_ids], dtype=float)

        t_start, t_end = t_span
        start_wall_time = time.time()

        if solver.upper() == "RK4":
            times, states = RK4Integrator.solve(self.evaluator.derivatives, t_span, y0, dt=dt)
        elif solver.upper() == "RKF45":
            times, states = AdaptiveRKSolver.solve(self.evaluator.derivatives, t_span, y0, tol=rtol)
        else:
            # Standard SciPy solve_ivp backend (LSODA, RK45, BDF)
            t_eval = np.linspace(t_start, t_end, int(np.ceil((t_end - t_start) / dt)) + 1)
            method = solver if solver in ["RK45", "RK23", "DOP853", "Radau", "BDF", "LSODA"] else "LSODA"
            sol = solve_ivp(
                fun=self.evaluator.derivatives,
                t_span=t_span,
                y0=y0,
                method=method,
                t_eval=t_eval,
                rtol=rtol,
                atol=atol,
            )
            times = sol.t
            states = sol.y.T  # Transpose to (n_times, n_species)

        elapsed = time.time() - start_wall_time

        # Build trajectory dict
        trajectories: Dict[str, List[float]] = {}
        for idx, s_id in enumerate(species_ids):
            # Non-negative clean representation
            trajectories[s_id] = [max(0.0, float(val)) for val in states[:, idx]]

        # Assess steady state by checking derivative norm at final point
        final_derivatives = self.evaluator.derivatives(times[-1], states[-1])
        derivative_norm = float(np.linalg.norm(final_derivatives))
        is_steady = bool(derivative_norm < 1e-4)

        trajectory_obj = Trajectory(
            times=[float(t) for t in times],
            species_trajectories=trajectories,
            time_unit="second",
            concentration_unit="uM",
        )

        return SimulationResult(
            job_id=job_id,
            model_id=self.model.model_id,
            model_type=self.model.model_type,
            solver=solver,
            trajectory=trajectory_obj,
            execution_time_seconds=elapsed,
            is_steady_state=is_steady,
            metrics={
                "time_points": len(times),
                "derivative_norm_final": derivative_norm,
                "is_steady_state": is_steady,
            },
        )
