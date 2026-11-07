"""Biological plausibility checks and expected qualitative perturbation directions."""

from typing import Any, Dict, List, Tuple
from ai.cellular_simulation.schema import ValidationReport


class BiologicalPlausibilityValidator:
    """Verifies that model responses match expected biological qualitative behaviors."""

    @staticmethod
    def verify_perturbation_direction(
        wild_type_final: float,
        perturbed_final: float,
        expected_direction: str = "DECREASE", # "DECREASE", "INCREASE", or "UNCHANGED"
        target_name: str = "Phospho-ERK",
    ) -> Dict[str, Any]:
        """Check whether perturbation caused the expected qualitative shift in output species."""
        diff = perturbed_final - wild_type_final
        actual_direction = "UNCHANGED"
        if diff > 1e-6:
            actual_direction = "INCREASE"
        elif diff < -1e-6:
            actual_direction = "DECREASE"

        passed = (actual_direction == expected_direction.upper())

        return {
            "target": target_name,
            "expected_direction": expected_direction.upper(),
            "actual_direction": actual_direction,
            "passed": passed,
            "wild_type_value": wild_type_final,
            "perturbed_value": perturbed_final,
            "delta": diff,
        }
