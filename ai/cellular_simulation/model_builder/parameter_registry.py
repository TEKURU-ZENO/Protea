"""Parameter Registry tracking kinetic constants, bounds, and provenance."""

from __future__ import annotations

from typing import Dict, List, Optional
from ai.cellular_simulation.schema import Parameter, ParameterProvenance


class ParameterRegistry:
    """Stores and validates kinetic parameters for simulation models."""

    def __init__(self) -> None:
        self._parameters: Dict[str, Parameter] = {}

    def register_parameter(
        self,
        name: str,
        value: float,
        unit: str = "s^-1",
        lower_bound: Optional[float] = None,
        upper_bound: Optional[float] = None,
        provenance: str = ParameterProvenance.LITERATURE.value,
        description: str = ""
    ) -> Parameter:
        """Registers a parameter with validation bounds."""
        lb = lower_bound if lower_bound is not None else max(0.0, value * 0.1)
        ub = upper_bound if upper_bound is not None else value * 10.0

        param = Parameter(
            name=name,
            value=value,
            unit=unit,
            lower_bound=lb,
            upper_bound=ub,
            provenance=provenance,
            description=description
        )
        self._parameters[name] = param
        return param

    def get_parameter(self, name: str) -> Optional[Parameter]:
        return self._parameters.get(name)

    def get_all_parameters(self) -> Dict[str, Parameter]:
        return dict(self._parameters)


ParameterStore = ParameterRegistry

