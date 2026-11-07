"""
PROTEA AI Scientist - Experiment Design Agent
Designs controlled in-silico experiments with negative, positive, vehicle, and orthogonal controls.
"""

from typing import Dict, Any, List
from ai.ai_scientist.experiment_design.planner import ExperimentPlanner
from ai.ai_scientist.experiment_design.protocol_validator import ProtocolValidator


class ExperimentAgent:
    """
    Translates hypotheses into rigorously controlled, executable computational experiment plans.
    """

    def __init__(self):
        self.planner = ExperimentPlanner()
        self.validator = ProtocolValidator()

    def run(
        self,
        hypothesis: Any,
        target_entities: List[str],
        computational_engine: str = "CellularSimulationEngine",
    ) -> Dict[str, Any]:
        """
        Executes experiment planning and validation.
        """
        plan = self.planner.plan_experiment(
            hypothesis=hypothesis,
            target_entities=target_entities,
            computational_engine=computational_engine,
        )

        validation = self.validator.validate(plan)

        return {
            "plan": plan.dict() if hasattr(plan, "dict") else plan,
            "validation": validation,
            "is_valid": validation["is_valid"],
            "requires_human_approval": plan.requires_human_approval if hasattr(plan, "requires_human_approval") else False,
        }
