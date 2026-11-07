"""Data Leakage and Integrity Guardrails."""

from __future__ import annotations

import logging
from typing import Dict, List, Set

logger = logging.getLogger(__name__)


class LeakageChecker:
    """Enforces strict scientific train/test splitting and leakage prevention rules."""

    def verify_sample_disjointness(
        self,
        train_samples: Set[str],
        test_samples: Set[str]
    ) -> bool:
        """Ensures zero overlap between training and testing biological sample IDs."""
        overlap = train_samples.intersection(test_samples)
        if overlap:
            logger.error(f"Data leakage detected! Overlapping sample IDs: {overlap}")
            return False
        return True

    def verify_temporal_holdout(
        self,
        train_timepoints: List[float],
        test_timepoints: List[float]
    ) -> bool:
        """Ensures test observations occur strictly after train observations for forecasting."""
        max_train = max(train_timepoints) if train_timepoints else 0.0
        min_test = min(test_timepoints) if test_timepoints else 0.0
        if min_test <= max_train:
            logger.error(f"Temporal leakage detected: test timepoint {min_test} <= max train {max_train}")
            return False
        return True
