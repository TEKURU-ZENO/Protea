"""Change-Point Detection and Trajectory Divergence Analyzer."""

from __future__ import annotations

import math
from typing import Any, Dict, List
from ai.digital_twin.schema import TemporalObservation


class ChangeDetectionEngine:
    """Detects biological inflection points, acute response peaks, and steady-state transitions."""

    def __init__(self, velocity_threshold: float = 0.50):
        self.velocity_threshold = velocity_threshold

    def detect_change_points(
        self,
        time_series: List[TemporalObservation],
        feature: str = "gene_expression"
    ) -> List[Dict[str, Any]]:
        """Identifies timepoints with maximum rate of change (first derivative peaks)."""
        if len(time_series) < 2:
            return []

        sorted_ts = sorted(time_series, key=lambda x: x.timepoint)
        change_points: List[Dict[str, Any]] = []

        for i in range(1, len(sorted_ts)):
            t_prev = sorted_ts[i - 1]
            t_curr = sorted_ts[i]
            dt = t_curr.timepoint - t_prev.timepoint
            if dt <= 0:
                continue

            entity_shifts: List[Dict[str, Any]] = []
            for node, curr_state in t_curr.states.items():
                prev_state = t_prev.states.get(node)
                if not prev_state:
                    continue
                v_curr = getattr(curr_state, feature, None)
                v_prev = getattr(prev_state, feature, None)
                if v_curr is not None and v_prev is not None:
                    delta = v_curr - v_prev
                    velocity = delta / dt
                    if abs(velocity) >= self.velocity_threshold:
                        entity_shifts.append({
                            "entity": node,
                            "delta": round(delta, 2),
                            "velocity": round(velocity, 3)
                        })

            if entity_shifts:
                change_points.append({
                    "interval": (t_prev.timepoint, t_curr.timepoint),
                    "duration_hours": round(dt, 2),
                    "significantly_shifted_count": len(entity_shifts),
                    "top_responders": sorted(entity_shifts, key=lambda x: abs(x["velocity"]), reverse=True)[:5]
                })

        return change_points
