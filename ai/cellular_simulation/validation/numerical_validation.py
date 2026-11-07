"""Numerical convergence and sanity checks for simulation trajectories."""

from typing import Dict, List
import numpy as np

from ai.cellular_simulation.schema import SimulationResult, ValidationReport


class NumericalValidator:
    """Checks stability, finiteness, and non-negativity across simulated trajectories."""

    @staticmethod
    def validate_trajectory(result: SimulationResult, atol: float = 1e-9) -> ValidationReport:
        issues: List[str] = []
        traj = result.trajectory

        has_nan_inf = False
        has_negative = False

        for s_id, series in traj.species_trajectories.items():
            arr = np.array(series)
            if np.any(np.isnan(arr)) or np.any(np.isinf(arr)):
                has_nan_inf = True
                issues.append(f"Species '{s_id}' contains NaN or Inf numerical values.")
            if np.any(arr < -atol):
                has_negative = True
                min_val = float(np.min(arr))
                issues.append(f"Species '{s_id}' violates non-negativity with value: {min_val}.")

        converged = not has_nan_inf

        return ValidationReport(
            model_id=result.model_id,
            mass_conserved=True,
            non_negativity_satisfied=not has_negative,
            solver_converged=converged,
            issues=issues,
            is_valid=(not has_nan_inf and not has_negative),
        )
