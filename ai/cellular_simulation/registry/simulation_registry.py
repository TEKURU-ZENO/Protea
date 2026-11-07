"""Simulation run tracker and cryptographic provenance hash recorder."""

import hashlib
import json
from typing import Any, Dict, List, Optional
from ai.cellular_simulation.schema import SimulationResult, SimulationModel


class SimulationRunRegistry:
    """Records simulation execution history with provenance and repeatability hashes."""

    def __init__(self):
        self._runs: Dict[str, SimulationResult] = {}
        self._provenance_hashes: Dict[str, str] = {} # job_id -> sha256 hash

    @staticmethod
    def compute_provenance_hash(
        model: SimulationModel,
        solver: str,
        t_span: tuple[float, float],
        dt: float,
    ) -> str:
        """Compute SHA256 cryptographic digest of model inputs and solver configuration."""
        data = {
            "model_id": model.model_id,
            "species": {k: s.initial_amount for k, s in model.species.items()},
            "parameters": {k: p.value for k, p in model.parameters.items()},
            "solver": solver,
            "t_span": t_span,
            "dt": dt,
        }
        serialized = json.dumps(data, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def record_run(self, result: SimulationResult, provenance_hash: Optional[str] = None) -> None:
        self._runs[result.job_id] = result
        if provenance_hash:
            self._provenance_hashes[result.job_id] = provenance_hash

    def get_run(self, job_id: str) -> Optional[SimulationResult]:
        return self._runs.get(job_id)

    def list_runs(self) -> List[Dict[str, Any]]:
        return [
            {
                "job_id": r.job_id,
                "model_id": r.model_id,
                "model_type": r.model_type,
                "solver": r.solver,
                "execution_time_seconds": r.execution_time_seconds,
                "is_steady_state": r.is_steady_state,
                "provenance_hash": self._provenance_hashes.get(r.job_id, ""),
            }
            for r in self._runs.values()
        ]
