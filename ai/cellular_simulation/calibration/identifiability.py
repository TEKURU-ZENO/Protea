"""Identifiability analysis and profile likelihood evaluation."""

from typing import Any, Callable, Dict, List, Tuple
import numpy as np


class IdentifiabilityAnalyzer:
    """Evaluates whether parameters are uniquely identifiable from available data."""

    @staticmethod
    def profile_likelihood_scan(
        eval_objective: Callable[[Dict[str, float]], float],
        base_params: Dict[str, float],
        target_param: str,
        scan_multipliers: List[float] = [0.2, 0.5, 0.8, 1.0, 1.2, 1.5, 2.0, 5.0],
    ) -> Dict[str, Any]:
        """Scan target parameter across multipliers while keeping others fixed to profile likelihood curvature."""
        base_val = base_params[target_param]
        param_values = [base_val * m for m in scan_multipliers]
        objective_values = []

        for val in param_values:
            test_params = dict(base_params)
            test_params[target_param] = val
            obj_val = eval_objective(test_params)
            objective_values.append(obj_val)

        min_idx = int(np.argmin(objective_values))
        curvature = 0.0
        if len(objective_values) >= 3:
            # Second difference around minimum
            diffs = np.gradient(objective_values)
            curvature = float(np.mean(np.abs(np.diff(diffs))))

        is_practically_identifiable = curvature > 1e-4

        return {
            "target_parameter": target_param,
            "parameter_values": param_values,
            "objective_values": objective_values,
            "curvature": curvature,
            "is_practically_identifiable": is_practically_identifiable,
        }
