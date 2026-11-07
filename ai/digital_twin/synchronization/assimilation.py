"""Data Assimilation Engine incorporating new measurements into dynamic twin states."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from ai.digital_twin.schema import MolecularState

logger = logging.getLogger(__name__)


class DataAssimilator:
    """Performs recursive state assimilation using Kalman filtering and Bayesian updates."""

    def __init__(self, process_variance: float = 0.05, default_measurement_variance: float = 0.15):
        self.q = process_variance  # Process noise variance
        self.r = default_measurement_variance  # Measurement noise variance

    def assimilate_kalman(
        self,
        prior_state: MolecularState,
        measurement_value: float,
        measurement_variance: Optional[float] = None,
        feature: str = "gene_expression"
    ) -> MolecularState:
        """Applies 1D Kalman filter to update state estimate and reduce variance."""
        prior_val = getattr(prior_state, feature, None)
        if prior_val is None:
            setattr(prior_state, feature, measurement_value)
            return prior_state

        r_actual = measurement_variance or self.r
        p_prior = (1.0 - prior_state.confidence) ** 2 + self.q

        # Kalman gain: K = P_prior / (P_prior + R)
        kalman_gain = p_prior / (p_prior + r_actual)

        # Posterior state: x_post = x_prior + K * (z - x_prior)
        posterior_val = prior_val + kalman_gain * (measurement_value - prior_val)
        posterior_variance = (1.0 - kalman_gain) * p_prior

        setattr(prior_state, feature, round(posterior_val, 3))
        # Updated confidence
        prior_state.confidence = round(max(0.1, min(1.0, 1.0 - (posterior_variance ** 0.5))), 3)
        return prior_state
