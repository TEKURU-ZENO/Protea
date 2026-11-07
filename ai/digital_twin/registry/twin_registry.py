"""Digital Twin Registry catalog managing live twin instances."""

from __future__ import annotations

import logging
from typing import Dict, List, Optional
from ai.digital_twin.schema import DigitalTwin

logger = logging.getLogger(__name__)


class TwinRegistryCatalog:
    """Manages active digital twin registrations, querying by organism, tissue, and tags."""

    def __init__(self) -> None:
        self._twins: Dict[str, DigitalTwin] = {}

    def register(self, twin: DigitalTwin) -> None:
        self._twins[twin.twin_id] = twin
        logger.info(f"Registered twin {twin.twin_id} in catalog.")

    def get(self, twin_id: str) -> Optional[DigitalTwin]:
        return self._twins.get(twin_id)

    def list_all(self) -> List[DigitalTwin]:
        return list(self._twins.values())

    def filter_twins(
        self,
        organism: Optional[str] = None,
        tissue: Optional[str] = None,
        cell_type: Optional[str] = None
    ) -> List[DigitalTwin]:
        results = list(self._twins.values())
        if organism:
            results = [t for t in results if t.organism.lower() == organism.lower()]
        if tissue:
            results = [t for t in results if t.primary_tissue.lower() == tissue.lower()]
        if cell_type:
            results = [t for t in results if t.primary_cell_type.lower() == cell_type.lower()]
        return results

    def remove(self, twin_id: str) -> bool:
        if twin_id in self._twins:
            del self._twins[twin_id]
            return True
        return False
