"""Central Registry Hub for Phase 7 Digital Interactome Twin."""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Optional

from ai.digital_twin.schema import DigitalTwin, TwinVersion

logger = logging.getLogger(__name__)


class DigitalTwinRegistry:
    """Singleton registry tracking registered Digital Twin instances and component providers."""
    _instance: Optional[DigitalTwinRegistry] = None

    def __new__(cls) -> DigitalTwinRegistry:
        if cls._instance is None:
            cls._instance = super(DigitalTwinRegistry, cls).__new__(cls)
            cls._instance._twins: Dict[str, DigitalTwin] = {}
            cls._instance._initializers: Dict[str, Any] = {}
            cls._instance._interactome_builders: Dict[str, Any] = {}
            cls._instance._state_estimators: Dict[str, Any] = {}
            cls._instance._temporal_trackers: Dict[str, Any] = {}
            cls._instance._multiomics_integrators: Dict[str, Any] = {}
            cls._instance._assimilators: Dict[str, Any] = {}
            cls._instance._comparators: Dict[str, Any] = {}
            cls._instance._scenario_managers: Dict[str, Any] = {}
            cls._instance._validators: Dict[str, Any] = {}
        return cls._instance

    @classmethod
    def get_instance(cls) -> DigitalTwinRegistry:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # Twin Management
    def register_twin(self, twin: DigitalTwin) -> None:
        self._twins[twin.twin_id] = twin
        logger.info(f"Registered digital twin: {twin.twin_id} ({twin.name})")

    def get_twin(self, twin_id: str) -> Optional[DigitalTwin]:
        return self._twins.get(twin_id)

    def list_twins(self) -> List[DigitalTwin]:
        return list(self._twins.values())

    def delete_twin(self, twin_id: str) -> bool:
        if twin_id in self._twins:
            del self._twins[twin_id]
            return True
        return False

    def clear(self) -> None:
        self._twins.clear()

    # Component Factory Registrations
    def register_component(self, category: str, name: str, component: Any) -> None:
        attr_name = f"_{category}"
        if hasattr(self, attr_name):
            getattr(self, attr_name)[name] = component
            logger.info(f"Registered {category} component: {name}")
        else:
            raise ValueError(f"Unknown component category: {category}")

    def get_component(self, category: str, name: str) -> Optional[Any]:
        attr_name = f"_{category}"
        if hasattr(self, attr_name):
            return getattr(self, attr_name).get(name)
        return None
