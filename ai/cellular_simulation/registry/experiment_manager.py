"""Multi-condition in-silico experiment management and comparison."""

from typing import Any, Dict, List, Optional
from ai.cellular_simulation.schema import SimulationResult


class ExperimentManager:
    """Manages batches of simulation runs and comparative condition studies."""

    def __init__(self):
        self._experiments: Dict[str, Dict[str, Any]] = {}

    def create_experiment(
        self,
        experiment_id: str,
        name: str,
        description: str = "",
    ) -> None:
        self._experiments[experiment_id] = {
            "experiment_id": experiment_id,
            "name": name,
            "description": description,
            "conditions": {}, # condition_name -> SimulationResult
        }

    def add_condition_result(
        self,
        experiment_id: str,
        condition_name: str,
        result: SimulationResult,
    ) -> None:
        if experiment_id in self._experiments:
            self._experiments[experiment_id]["conditions"][condition_name] = result

    def get_experiment_summary(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        exp = self._experiments.get(experiment_id)
        if not exp:
            return None

        condition_summaries = {}
        for cond_name, res in exp["conditions"].items():
            condition_summaries[cond_name] = {
                "job_id": res.job_id,
                "model_id": res.model_id,
                "solver": res.solver,
                "metrics": res.metrics,
            }

        return {
            "experiment_id": exp["experiment_id"],
            "name": exp["name"],
            "description": exp["description"],
            "conditions_count": len(exp["conditions"]),
            "conditions": condition_summaries,
        }
