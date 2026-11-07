"""
PROTEA AI Scientist - Parameter Sensitivity & Robustness Analysis
Evaluates perturbation stability, parameter sensitivity, and fragility across computational runs.
"""

from typing import Dict, Any, List, Optional
import numpy as np


class RobustnessAnalyzer:
    """
    Performs parameter sensitivity and perturbation stability analysis on in-silico experiments.
    """

    def __init__(self, sensitivity_threshold: float = 0.5):
        self.sensitivity_threshold = sensitivity_threshold

    def analyze_parameter_sensitivity(
        self,
        nominal_output: float,
        perturbed_evaluations: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Calculates normalized sensitivity coefficients S_ij = (dY/Y) / (dP/P).
        perturbed_evaluations: list of dicts with keys:
          'parameter_name': str
          'nominal_param_val': float
          'perturbed_param_val': float
          'perturbed_output': float
        """
        sensitivities = {}
        fragile_parameters = []

        if abs(nominal_output) < 1e-9:
            base_y = 1e-9
        else:
            base_y = nominal_output

        for item in perturbed_evaluations:
            p_name = item.get("parameter_name", "unknown")
            p_nom = float(item.get("nominal_param_val", 1.0))
            p_pert = float(item.get("perturbed_param_val", 1.0))
            y_pert = float(item.get("perturbed_output", nominal_output))

            delta_p = p_pert - p_nom
            if abs(delta_p) < 1e-9:
                rel_p = 1e-9
            else:
                rel_p = delta_p / (p_nom if abs(p_nom) > 1e-9 else 1.0)

            delta_y = y_pert - nominal_output
            rel_y = delta_y / base_y

            sensitivity_coeff = rel_y / rel_p if abs(rel_p) > 1e-9 else 0.0
            abs_s = abs(sensitivity_coeff)

            sensitivities[p_name] = {
                "sensitivity_coefficient": round(sensitivity_coeff, 4),
                "absolute_sensitivity": round(abs_s, 4),
                "parameter_variation_pct": round(rel_p * 100, 2),
                "output_response_pct": round(rel_y * 100, 2),
                "is_sensitive": abs_s > self.sensitivity_threshold,
            }

            if abs_s > self.sensitivity_threshold:
                fragile_parameters.append(p_name)

        # Compute overall robustness score: 1.0 - mean(min(1.0, abs_s))
        if sensitivities:
            mean_abs_s = float(np.mean([v["absolute_sensitivity"] for v in sensitivities.values()]))
            robustness_score = max(0.0, min(1.0, 1.0 - (mean_abs_s / 2.0)))
        else:
            robustness_score = 1.0

        return {
            "robustness_score": round(robustness_score, 4),
            "fragile_parameters": list(set(fragile_parameters)),
            "parameter_sensitivities": sensitivities,
            "conclusion": (
                "Robust across parameter ranges"
                if robustness_score >= 0.7
                else "Fragile; outcome is highly dependent on precise kinetic/topological parameters"
            ),
        }

    def evaluate_perturbation_stability(
        self,
        replicate_outcomes: List[float],
        tolerance_std_ratio: float = 0.25,
    ) -> Dict[str, Any]:
        """
        Evaluates stability across stochastic solver replicates.
        Note: Stochastically simulated replicates capture solver/numerical variance, not biological variance.
        """
        if not replicate_outcomes:
            return {"stability_score": 0.0, "status": "no_replicates"}

        arr = np.array(replicate_outcomes, dtype=float)
        mean_val = float(np.mean(arr))
        std_val = float(np.std(arr))
        cv = (std_val / abs(mean_val)) if abs(mean_val) > 1e-9 else float(std_val)

        is_stable = cv <= tolerance_std_ratio

        return {
            "stability_score": round(max(0.0, 1.0 - cv), 4),
            "mean_outcome": round(mean_val, 4),
            "standard_deviation": round(std_val, 4),
            "coefficient_of_variation": round(cv, 4),
            "is_stable": is_stable,
            "note": "Replicate simulations evaluate numerical stability, not independent biological replication.",
        }
