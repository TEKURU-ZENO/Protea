"""
PROTEA BRE - Uncertainty Quantification & Scientific Calibration
Calculates Expected Calibration Error (ECE), Brier score, and evidence coverage metrics.
"""

from typing import List, Dict, Tuple, Any
import numpy as np

def calculate_brier_score(probabilities: List[float], outcomes: List[int]) -> float:
    """Calculate Brier score: mean squared difference between predicted probabilities and binary outcomes."""
    if not probabilities or len(probabilities) != len(outcomes):
        return 0.0
    p = np.array(probabilities, dtype=float)
    y = np.array(outcomes, dtype=float)
    return float(np.mean((p - y) ** 2))

def calculate_expected_calibration_error(probabilities: List[float], outcomes: List[int], n_bins: int = 10) -> float:
    """
    Calculate Expected Calibration Error (ECE):
    ECE = sum_{b=1}^B (|B_b| / N) * |acc(B_b) - conf(B_b)|
    """
    if not probabilities or len(probabilities) != len(outcomes):
        return 0.0

    p = np.array(probabilities, dtype=float)
    y = np.array(outcomes, dtype=float)
    N = len(p)

    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0

    for i in range(n_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]

        in_bin = (p >= bin_lower) & (p < bin_upper if i < n_bins - 1 else p <= bin_upper)
        bin_size = np.sum(in_bin)

        if bin_size > 0:
            bin_acc = np.mean(y[in_bin])
            bin_conf = np.mean(p[in_bin])
            ece += (bin_size / N) * abs(bin_acc - bin_conf)

    return float(round(ece, 4))


class UncertaintyEstimator:
    """Evaluates evidence coverage, flags missing context, and quantifies model certainty."""

    def evaluate_uncertainty(
        self,
        target: str,
        evidence_count: int,
        compartment_known: bool,
        tissue_specified: bool,
        has_contradictions: bool
    ) -> Dict[str, Any]:
        """Quantify overall uncertainty and emit missing-context caveats."""
        warnings = []
        uncertainty_penalty = 0.0

        if evidence_count < 3:
            warnings.append(f"Low empirical evidence volume ({evidence_count} observations) for {target}.")
            uncertainty_penalty += 0.25

        if not compartment_known:
            warnings.append(f"Subcellular localization for {target} is unverified.")
            uncertainty_penalty += 0.15

        if not tissue_specified:
            warnings.append("No specific tissue context provided; mechanism assumes generalized in vitro physiological state.")
            uncertainty_penalty += 0.10

        if has_contradictions:
            warnings.append("Opposing literature claims detected for one or more steps in the mechanism.")
            uncertainty_penalty += 0.30

        calibrated_confidence = round(max(0.15, min(0.95, 1.0 - uncertainty_penalty)), 3)

        return {
            "calibrated_confidence": calibrated_confidence,
            "uncertainty_score": round(1.0 - calibrated_confidence, 3),
            "evidence_coverage": "Comprehensive" if evidence_count >= 5 else ("Moderate" if evidence_count >= 2 else "Sparse"),
            "context_warnings": warnings
        }
