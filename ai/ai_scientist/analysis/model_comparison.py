"""Model selection and information criterion scoring."""

import numpy as np
from typing import Dict, Any


class ModelComparisonEvaluator:
    """Evaluates Akaike Information Criterion (AIC) and Bayesian Information Criterion (BIC)."""

    @staticmethod
    def compare_models(
        sse_model1: float,
        k_params1: int,
        sse_model2: float,
        k_params2: int,
        n_points: int = 50,
    ) -> Dict[str, Any]:
        """Compute AIC and BIC for competing mechanistic models."""
        aic1 = n_points * np.log(max(1e-12, sse_model1 / n_points)) + 2 * k_params1
        aic2 = n_points * np.log(max(1e-12, sse_model2 / n_points)) + 2 * k_params2

        bic1 = n_points * np.log(max(1e-12, sse_model1 / n_points)) + k_params1 * np.log(n_points)
        bic2 = n_points * np.log(max(1e-12, sse_model2 / n_points)) + k_params2 * np.log(n_points)

        delta_aic = float(aic2 - aic1)
        preferred_model = "Model 1" if delta_aic > 2.0 else "Model 2" if delta_aic < -2.0 else "Inconclusive"

        return {
            "model1_aic": round(float(aic1), 2),
            "model2_aic": round(float(aic2), 2),
            "delta_aic": round(delta_aic, 2),
            "preferred_model": preferred_model,
        }


ModelComparisonEngine = ModelComparisonEvaluator
