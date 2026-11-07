"""Time Series data structures tracking temporal molecular trajectories."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from ai.digital_twin.schema import MolecularState, TemporalObservation

logger = logging.getLogger(__name__)


class TimeSeriesTracker:
    """Manages longitudinal molecular measurements and irregular sampling schedules."""

    def __init__(self) -> None:
        pass

    def sort_time_series(self, observations: List[TemporalObservation]) -> List[TemporalObservation]:
        """Ensures observations are strictly ordered by timepoint."""
        return sorted(observations, key=lambda x: x.timepoint)

    def extract_entity_trajectory(
        self,
        observations: List[TemporalObservation],
        entity_id: str,
        feature: str = "gene_expression"
    ) -> List[Dict[str, Any]]:
        """Extracts the time trajectory of a specific molecular entity."""
        sorted_obs = self.sort_time_series(observations)
        trajectory: List[Dict[str, Any]] = []

        for obs in sorted_obs:
            state = obs.states.get(entity_id)
            val = getattr(state, feature, None) if state else None
            trajectory.append({
                "timepoint": obs.timepoint,
                "unit": obs.unit,
                "value": val,
                "status": state.status if state else "MISSING"
            })

        return trajectory
