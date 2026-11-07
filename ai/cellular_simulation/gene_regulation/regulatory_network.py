"""Gene Regulatory Network simulation orchestrator."""

import time
import uuid
from typing import Dict, List, Optional, Tuple
import numpy as np

from ai.cellular_simulation.schema import SimulationModel, SimulationResult, Trajectory
from ai.cellular_simulation.deterministic.ode_engine import ODEDynamicsEngine
from ai.cellular_simulation.gene_regulation.boolean_model import BooleanNetwork


class RegulatoryNetworkEngine:
    """Simulates Gene Regulatory Networks across continuous ODE and discrete Boolean formalisms."""

    def __init__(self, model: SimulationModel):
        self.model = model
        self.ode_engine = ODEDynamicsEngine(model)

    def simulate_continuous(
        self,
        t_span: Tuple[float, float] = (0.0, 100.0),
        dt: float = 0.2,
        solver: str = "LSODA",
        job_id: Optional[str] = None,
    ) -> SimulationResult:
        """Run continuous regulatory simulation using Hill-type ODE equations."""
        result = self.ode_engine.simulate(t_span=t_span, dt=dt, solver=solver, job_id=job_id)
        result.model_type = "REGULATORY"
        return result

    def simulate_boolean_approximation(
        self,
        threshold: float = 0.5,
        steps: int = 20,
    ) -> List[Dict[str, int]]:
        """Binarize network states and simulate discrete Boolean transitions."""
        gene_names = list(self.model.species.keys())
        initial_bin = {
            g: (1 if self.model.species[g].initial_amount >= threshold else 0)
            for g in gene_names
        }

        # Build simple threshold activation rule
        rules = {}
        for g in gene_names:
            rules[g] = lambda s, gene=g: 1 if s.get(gene, 0) == 1 else 0

        bn = BooleanNetwork(gene_names, rules)
        return bn.simulate(initial_bin, steps=steps)
