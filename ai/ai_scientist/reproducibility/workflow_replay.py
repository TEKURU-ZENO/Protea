"""
PROTEA AI Scientist - Deterministic Workflow Replay
Re-executes computational pipelines and verifies deterministic repeatability.
"""

from typing import Dict, Any, List
import numpy as np


class WorkflowReplayEngine:
    """
    Enables one-click replay of computational experiments to verify exact reproducibility.
    """

    def verify_reproducibility(
        self,
        original_outputs: List[float],
        replay_outputs: List[float],
        tolerance: float = 1e-6,
    ) -> Dict[str, Any]:
        """
        Compares original and replayed numeric outcomes.
        """
        if len(original_outputs) != len(replay_outputs):
            return {
                "reproducible": False,
                "reason": f"Length mismatch: {len(original_outputs)} vs {len(replay_outputs)}",
                "max_absolute_error": float("inf"),
            }

        orig_arr = np.array(original_outputs, dtype=float)
        rep_arr = np.array(replay_outputs, dtype=float)

        abs_diff = np.abs(orig_arr - rep_arr)
        max_err = float(np.max(abs_diff)) if len(abs_diff) > 0 else 0.0
        mean_err = float(np.mean(abs_diff)) if len(abs_diff) > 0 else 0.0

        is_reproducible = bool(max_err <= tolerance)

        return {
            "reproducible": is_reproducible,
            "max_absolute_error": round(max_err, 8),
            "mean_absolute_error": round(mean_err, 8),
            "tolerance": tolerance,
            "status": "PASS" if is_reproducible else "DIVERGENCE_DETECTED",
        }
