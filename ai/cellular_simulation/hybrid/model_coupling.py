"""Coupling rules between heterogeneous formalisms (Signaling, GRN, Metabolism)."""

from typing import Any, Callable, Dict, List
from ai.cellular_simulation.schema import SimulationModel


class ModelCouplingLink:
    """Couples an output species from a source model to an input/boundary in a target model."""

    def __init__(
        self,
        source_model_id: str,
        source_variable: str,
        target_model_id: str,
        target_variable: str,
        transfer_function: Callable[[float], float] = lambda x: x,
        coupling_type: str = "concentration_to_promoter", # or "enzyme_to_flux_bound"
    ):
        self.source_model_id = source_model_id
        self.source_variable = source_variable
        self.target_model_id = target_model_id
        self.target_variable = target_variable
        self.transfer_function = transfer_function
        self.coupling_type = coupling_type

    def transfer(self, source_value: float) -> float:
        """Apply transfer function mapping source state to target parameter or species."""
        return self.transfer_function(source_value)
