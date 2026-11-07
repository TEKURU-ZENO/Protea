"""Digital Twin Evaluation Metrics library."""

from __future__ import annotations

import math
from typing import Dict, List, Tuple


def calculate_mae(predictions: List[float], targets: List[float]) -> float:
    if not predictions:
        return 0.0
    return round(sum(abs(p - t) for p, t in zip(predictions, targets)) / len(predictions), 4)


def calculate_rmse(predictions: List[float], targets: List[float]) -> float:
    if not predictions:
        return 0.0
    return round(math.sqrt(sum((p - t) ** 2 for p, t in zip(predictions, targets)) / len(predictions)), 4)


def calculate_spearman_rho(predictions: List[float], targets: List[float]) -> float:
    n = len(predictions)
    if n < 2:
        return 1.0

    rank_p = [sorted(predictions).index(x) for x in predictions]
    rank_t = [sorted(targets).index(x) for x in targets]

    d_sq = sum((rp - rt) ** 2 for rp, rt in zip(rank_p, rank_t))
    rho = 1.0 - (6.0 * d_sq) / (n * (n ** 2 - 1))
    return round(rho, 4)


def calculate_brier_score(probabilities: List[float], outcomes: List[int]) -> float:
    if not probabilities:
        return 0.0
    return round(sum((p - o) ** 2 for p, o in zip(probabilities, outcomes)) / len(probabilities), 4)


def calculate_ece(probabilities: List[float], outcomes: List[int], n_bins: int = 10) -> float:
    if not probabilities:
        return 0.0

    bin_size = 1.0 / n_bins
    ece = 0.0
    n = len(probabilities)

    for i in range(n_bins):
        bin_lower = i * bin_size
        bin_upper = (i + 1) * bin_size
        bin_indices = [idx for idx, p in enumerate(probabilities) if bin_lower <= p < bin_upper]

        if not bin_indices:
            continue

        bin_conf = sum(probabilities[idx] for idx in bin_indices) / len(bin_indices)
        bin_acc = sum(outcomes[idx] for idx in bin_indices) / len(bin_indices)
        ece += (len(bin_indices) / n) * abs(bin_acc - bin_conf)

    return round(ece, 4)
