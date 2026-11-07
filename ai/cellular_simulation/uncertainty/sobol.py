"""Variance-based Global Sensitivity Analysis (Sobol indices)."""

from typing import Callable, Dict, List, Tuple
import numpy as np


class SobolSensitivityAnalyzer:
    """Computes first-order (S_i) and total (S_Ti) Sobol indices via Saltelli sampling."""

    @staticmethod
    def calculate_indices(
        model_evaluator: Callable[[List[float]], float], # maps parameter vector to scalar response
        param_bounds: List[Tuple[float, float]],
        num_samples: int = 128,
        seed: int = 42,
    ) -> Dict[str, List[float]]:
        rng = np.random.RandomState(seed)
        d = len(param_bounds)

        # Generate sample matrices A and B
        A = np.zeros((num_samples, d))
        B = np.zeros((num_samples, d))

        for j in range(d):
            lb, ub = param_bounds[j]
            A[:, j] = rng.uniform(lb, ub, num_samples)
            B[:, j] = rng.uniform(lb, ub, num_samples)

        # Evaluate f(A) and f(B)
        y_A = np.array([model_evaluator(list(A[i])) for i in range(num_samples)])
        y_B = np.array([model_evaluator(list(B[i])) for i in range(num_samples)])

        var_total = np.var(np.concatenate([y_A, y_B]))
        if var_total <= 1e-12:
            return {"S1": [0.0] * d, "ST": [0.0] * d}

        S1 = []
        ST = []

        for j in range(d):
            # Matrix C_j: A with column j from B
            C_j = np.copy(A)
            C_j[:, j] = B[:, j]
            y_Cj = np.array([model_evaluator(list(C_j[i])) for i in range(num_samples)])

            # First-order index S_j
            v_j = np.mean(y_B * (y_Cj - y_A))
            s1_j = float(v_j / var_total)

            # Total-order index ST_j
            v_tj = 0.5 * np.mean((y_A - y_Cj) ** 2)
            st_j = float(v_tj / var_total)

            S1.append(max(0.0, s1_j))
            ST.append(max(0.0, st_j))

        return {"S1": S1, "ST": ST}
