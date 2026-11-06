"""
PROTEA PaIE - Multiple Testing Correction & Statistical Utilities
Provides Benjamini-Hochberg False Discovery Rate (FDR) and Bonferroni adjustments.
"""

from typing import List, Tuple
import numpy as np

def benjamini_hochberg(p_values: List[float]) -> List[float]:
    """
    Apply Benjamini-Hochberg False Discovery Rate (FDR) correction to p-values.
    Returns list of adjusted p-values (q-values) preserving original order.
    """
    n = len(p_values)
    if n == 0:
        return []
    if n == 1:
        return [min(1.0, max(0.0, p_values[0]))]

    p_arr = np.array(p_values, dtype=float)
    # Get sort indices
    order = np.argsort(p_arr)
    ranked_p = p_arr[order]

    # Calculate q_i = p_i * n / rank
    ranks = np.arange(1, n + 1)
    q_values = ranked_p * n / ranks

    # Ensure monotonicity from right to left: q_i = min(q_i, q_{i+1})
    for i in range(n - 2, -1, -1):
        q_values[i] = min(q_values[i], q_values[i + 1])

    # Cap at 1.0
    q_values = np.clip(q_values, 0.0, 1.0)

    # Restore original input order
    adj_p = np.empty(n, dtype=float)
    adj_p[order] = q_values
    return adj_p.tolist()

def bonferroni(p_values: List[float]) -> List[float]:
    """Apply Bonferroni Family-Wise Error Rate (FWER) correction."""
    n = len(p_values)
    return [min(1.0, p * n) for p in p_values]
