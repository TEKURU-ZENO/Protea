"""State Trajectory Interpolator and Forward Forecaster."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from ai.digital_twin.schema import MolecularState, TemporalObservation

logger = logging.getLogger(__name__)


class TrajectoryForecaster:
    """Interpolates irregular timecourses and projects short-horizon state trajectories."""

    def interpolate_state(
        self,
        time_series: List[TemporalObservation],
        query_timepoint: float,
        entity_id: str,
        feature: str = "gene_expression"
    ) -> Optional[float]:
        """Performs piecewise linear interpolation between adjacent observation points."""
        if not time_series:
            return None

        sorted_ts = sorted(time_series, key=lambda x: x.timepoint)

        # Boundary checks
        if query_timepoint <= sorted_ts[0].timepoint:
            s = sorted_ts[0].states.get(entity_id)
            return getattr(s, feature, None) if s else None

        if query_timepoint >= sorted_ts[-1].timepoint:
            s = sorted_ts[-1].states.get(entity_id)
            return getattr(s, feature, None) if s else None

        # Find enclosing bracket
        for i in range(len(sorted_ts) - 1):
            t1 = sorted_ts[i]
            t2 = sorted_ts[i + 1]
            if t1.timepoint <= query_timepoint <= t2.timepoint:
                s1 = t1.states.get(entity_id)
                s2 = t2.states.get(entity_id)
                v1 = getattr(s1, feature, None) if s1 else None
                v2 = getattr(s2, feature, None) if s2 else None
                if v1 is None or v2 is None:
                    return v1 or v2
                # Linear fraction
                alpha = (query_timepoint - t1.timepoint) / (t2.timepoint - t1.timepoint)
                return round(v1 + alpha * (v2 - v1), 3)

        return None
