"""Twin Version Manager tracking parent-child lineage and release history."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from ai.digital_twin.schema import DigitalTwin, TwinVersion

logger = logging.getLogger(__name__)


class TwinVersionManager:
    """Manages version lineage DAG, active version promotion, and version rollback."""

    def get_version_lineage(self, twin: DigitalTwin, version_id: str) -> List[TwinVersion]:
        """Traces back ancestry from a given version to the root version."""
        lineage: List[TwinVersion] = []
        curr_id: Optional[str] = version_id

        while curr_id and curr_id in twin.versions:
            v = twin.versions[curr_id]
            lineage.append(v)
            curr_id = v.parent_version_id

        return lineage

    def set_active_version(self, twin: DigitalTwin, version_id: str) -> bool:
        """Promotes a specific version to be the active runtime state of the twin."""
        if version_id in twin.versions:
            twin.active_version_id = version_id
            logger.info(f"Set active version for twin {twin.twin_id} to {version_id}.")
            return True
        return False
