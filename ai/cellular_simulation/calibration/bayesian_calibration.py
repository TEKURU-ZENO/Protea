"""Bayesian calibration and Markov Chain Monte Carlo (MCMC) parameter estimation."""

from typing import Any, Callable, Dict, List, Tuple
import numpy as np


class BayesianCalibrator:
    """MCMC posterior sampling for parameter uncertainty intervals."""

    @staticmethod
    def sample_posterior(
        log_likelihood_fn: Callable[[Dict[str, float]], float],
        initial_params: Dict[str, float],
        param_bounds: Dict[str, Tuple[float, float]],
        num_samples: int = 500,
        burn_in: int = 100,
        proposal_std: float = 0.05,
        random_seed: int = 42,
    ) -> Dict[str, Any]:
        """Metropolis-Hastings MCMC sampling of posterior parameter distributions."""
        rng = np.random.RandomState(random_seed)
        param_names = list(initial_params.keys())

        current = dict(initial_params)
        current_ll = log_likelihood_fn(current)

        chain = []
        accepted = 0

        for step in range(num_samples + burn_in):
            candidate = {}
            in_bounds = True
            for p in param_names:
                std = proposal_std * current[p]
                val = current[p] + rng.normal(0, max(1e-4, std))
                lb, ub = param_bounds.get(p, (1e-6, 1e4))
                if val < lb or val > ub:
                    in_bounds = False
                    break
                candidate[p] = val

            if in_bounds:
                candidate_ll = log_likelihood_fn(candidate)
                log_ratio = candidate_ll - current_ll
                if np.log(rng.uniform(1e-12, 1.0)) < log_ratio:
                    current = candidate
                    current_ll = candidate_ll
                    if step >= burn_in:
                        accepted += 1

            if step >= burn_in:
                chain.append(dict(current))

        # Compute 95% Credible Intervals
        credible_intervals = {}
        for p in param_names:
            vals = [s[p] for s in chain]
            credible_intervals[p] = {
                "mean": float(np.mean(vals)),
                "std": float(np.std(vals)),
                "ci_lower": float(np.percentile(vals, 2.5)),
                "ci_upper": float(np.percentile(vals, 97.5)),
            }

        acceptance_rate = accepted / max(1, num_samples)

        return {
            "samples": chain,
            "credible_intervals": credible_intervals,
            "acceptance_rate": acceptance_rate,
        }
