"""
PROTEA Phase 11: Multi-Omics Quality Control & Batch Diagnostics
Evaluates quality metrics and flags biological confounding with technical batch variables.
"""

from __future__ import annotations
from typing import Dict, List, Any, Optional
from ai.moeie.schema import OmicsMeasurement, BiologicalSample


class QualityControlEngine:
    """Evaluates multi-omics dataset quality and batch-effect confounding."""

    @classmethod
    def evaluate_quality(
        cls,
        measurements: List[OmicsMeasurement],
        samples: Optional[List[BiologicalSample]] = None
    ) -> Dict[str, Any]:
        """Calculates completeness, dynamic range, and outlier metrics."""
        total_m = len(measurements)
        if total_m == 0:
            return {"status": "EMPTY", "n_measurements": 0, "total_measurements": 0}

        missing_count = sum(1 for m in measurements if m.is_missing)
        missing_rate = round(missing_count / total_m, 4)

        raw_values = [m.raw_value for m in measurements if not m.is_missing]
        mean_val = round(sum(raw_values) / max(1, len(raw_values)), 2) if raw_values else 0.0
        max_val = max(raw_values) if raw_values else 0.0
        min_val = min(raw_values) if raw_values else 0.0

        # Quality flag counts
        flags: Dict[str, int] = {}
        for m in measurements:
            flags[m.quality_flag] = flags.get(m.quality_flag, 0) + 1

        qc_passed = missing_rate <= 0.40

        return {
            "status": "PASSED" if qc_passed else "FLAGGED",
            "total_measurements": total_m,
            "missing_rate": missing_rate,
            "mean_raw_intensity": mean_val,
            "min_raw_value": min_val,
            "max_raw_value": max_val,
            "quality_flag_distribution": flags,
            "recommendation": "Ready for downstream representation learning" if qc_passed else "Excessive missingness detected"
        }

    @classmethod
    def evaluate_batch_confounding(
        cls,
        samples: List[BiologicalSample]
    ) -> Dict[str, Any]:
        """
        Diagnoses whether biological conditions are confounded with technical batches.
        Severe confounding occurs when all disease samples are in batch A and all controls in batch B.
        """
        if not samples:
            return {"is_confounded": False, "confounding_score": 0.0}

        batch_condition_matrix: Dict[str, Dict[str, int]] = {}
        for s in samples:
            b = s.batch_id
            c = s.disease_state
            if b not in batch_condition_matrix:
                batch_condition_matrix[b] = {}
            batch_condition_matrix[b][c] = batch_condition_matrix[b].get(c, 0) + 1

        # Check overlap
        batches = list(batch_condition_matrix.keys())
        is_confounded = False
        confounding_score = 0.15

        if len(batches) > 1:
            # If any batch has only one condition, higher risk
            single_condition_batches = sum(1 for b in batches if len(batch_condition_matrix[b]) == 1)
            confounding_score = round(single_condition_batches / len(batches), 2)
            is_confounded = confounding_score >= 0.75

        return {
            "batches_analyzed": len(batches),
            "batch_condition_distribution": batch_condition_matrix,
            "confounding_score": confounding_score,
            "is_confounded": is_confounded,
            "warning": (
                "Caution: Biological condition is strongly confounded with technical batch. "
                "Blind batch correction may remove genuine biological signal."
                if is_confounded
                else "Acceptable batch mixing across biological conditions."
            )
        }
