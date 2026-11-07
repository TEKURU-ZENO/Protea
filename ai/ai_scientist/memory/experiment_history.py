"""
PROTEA AI Scientist - Experiment History Log
Maintains historical records of both positive and negative/falsified experiments.
"""

from typing import Dict, Any, List
import time


class ExperimentHistoryLog:
    """
    Maintains historical memory of experimental trials to prevent duplication of negative trials
    and reinforce successful experimental paradigms.
    """

    def __init__(self):
        self._history: List[Dict[str, Any]] = []

    def record_experiment(
        self,
        experiment_id: str,
        hypothesis_id: str,
        intervention: Dict[str, Any],
        outcome_metric: float,
        falsified: bool,
        notes: str = "",
    ) -> Dict[str, Any]:
        record = {
            "experiment_id": experiment_id,
            "hypothesis_id": hypothesis_id,
            "intervention": intervention,
            "outcome_metric": outcome_metric,
            "falsified": falsified,
            "notes": notes,
            "timestamp": time.time(),
        }
        self._history.append(record)
        return record

    def get_falsified_experiments(self) -> List[Dict[str, Any]]:
        return [e for e in self._history if e["falsified"]]

    def get_all(self) -> List[Dict[str, Any]]:
        return list(self._history)
