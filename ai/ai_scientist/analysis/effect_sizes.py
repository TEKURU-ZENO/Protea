"""Biophysical effect size and fold-change calculators."""

from typing import Dict, Any
import numpy as np


class EffectSizeCalculator:
    """Calculates standardized effect metrics including Cohen's d and log2 fold change."""

    @staticmethod
    def calculate_metrics(baseline: float, treated: float) -> Dict[str, float]:
        """Compute relative percentage reduction and log2 fold change."""
        abs_diff = treated - baseline
        pct_change = (abs_diff / max(1e-9, baseline)) * 100.0 if baseline > 0 else 0.0
        log2_fc = float(np.log2(max(1e-9, treated) / max(1e-9, baseline))) if baseline > 0 and treated > 0 else 0.0

        return {
            "absolute_difference": round(abs_diff, 4),
            "percentage_change": round(pct_change, 2),
            "log2_fold_change": round(log2_fc, 3),
            "relative_ratio": round(treated / max(1e-9, baseline), 4),
        }

    @classmethod
    def fold_change(cls, intervention_mean: float, control_mean: float) -> Dict[str, float]:
        """Calculates relative metrics given intervention mean and control mean."""
        return cls.calculate_metrics(baseline=control_mean, treated=intervention_mean)
