"""Monte Carlo parameter perturbation generator."""

from typing import Dict, List, Tuple
import numpy as np
from ai.cellular_simulation.schema import SimulationModel


class MonteCarloSampler:
    """Generates perturbed parameter sets using log-normal or uniform distributions."""

    @staticmethod
    def sample_parameters(
        base_parameters: Dict[str, float],
        num_samples: int = 50,
        coefficient_of_variation: float = 0.2, # 20% standard deviation relative to mean
        seed: int = 42,
    ) -> List[Dict[str, float]]:
        rng = np.random.RandomState(seed)
        samples = []

        param_names = list(base_parameters.keys())

        for _ in range(num_samples):
            p_set = {}
            for p in param_names:
                mu = base_parameters[p]
                sigma = coefficient_of_variation * max(1e-6, mu)
                # Sample log-normal to guarantee positive values
                log_mu = np.log(mu)
                log_sigma = np.sqrt(np.log(1.0 + (sigma / mu) ** 2))
                val = float(rng.lognormal(log_mu, log_sigma))
                p_set[p] = val
            samples.append(p_set)

        return samples
