"""Protocol safety and constraint validator."""

from typing import Any, Dict, List
from ai.ai_scientist.schema import ExperimentPlan


class ProtocolValidator:
    """Verifies that experimental protocols conform to safety and compute boundaries."""

    @staticmethod
    def validate_plan(plan: ExperimentPlan) -> Dict[str, Any]:
        issues: List[str] = []

        if not plan.target_entities:
            issues.append("Experiment plan specifies no target biological entities.")

        if plan.replicates < 1 or plan.replicates > 50:
            issues.append(f"Replicates count ({plan.replicates}) outside allowed range [1, 50].")

        if not plan.controls:
            issues.append("Missing required experimental controls (negative/vehicle baseline).")

        is_valid = len(issues) == 0

        return {
            "is_valid": is_valid,
            "experiment_id": plan.experiment_id,
            "issues": issues,
            "requires_human_approval": True,
        }

    @classmethod
    def validate(cls, plan: ExperimentPlan) -> Dict[str, Any]:
        return cls.validate_plan(plan)

