"""
PROTEA AI Scientist - Execution Agent
Dispatches computational workflows to PROTEA engines, enforcing compute budgets and approval gates.
"""

from typing import Dict, Any
from ai.ai_scientist.execution.workflow_executor import WorkflowExecutor
from ai.ai_scientist.execution.resource_manager import ResourceManager


class ExecutionAgent:
    """
    Supervises the execution of computational experiments on PROTEA engines.
    """

    def __init__(self, budget_minutes: float = 30.0):
        self.resource_manager = ResourceManager(max_runtime_minutes=budget_minutes)
        self.executor = WorkflowExecutor()

    def run(self, experiment_plan: Any, user_approved: bool = False) -> Dict[str, Any]:
        """
        Executes the planned computational experiment.
        """
        exec_record = self.executor.execute_experiment(
            experiment_plan=experiment_plan,
            user_approved=user_approved,
        )

        return {
            "execution_record": exec_record.dict() if hasattr(exec_record, "dict") else exec_record,
            "success": exec_record.success if hasattr(exec_record, "success") else False,
            "status": exec_record.status if hasattr(exec_record, "status") else "UNKNOWN",
        }
