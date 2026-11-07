"""Target intervention specification designer."""

from typing import Any, Dict, List


class InterventionDesigner:
    """Configures chemical, genetic, and multi-factor perturbation specs."""

    @staticmethod
    def create_intervention_spec(
        intervention_type: str,
        target_entities: List[str],
        strength: float = 0.8,
    ) -> Dict[str, Any]:
        """Construct validated intervention parameter payload."""
        return {
            "intervention_type": intervention_type.upper(),
            "target_entities": target_entities,
            "strength": max(0.0, min(1.0, strength)),
            "duration": 60.0,
            "mechanism": "competitive_enzymatic_inhibition" if intervention_type == "INHIBITION" else "loss_of_function",
        }
