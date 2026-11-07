"""Snapshot Archive Manager preserving content-hashed immutable network states."""

from __future__ import annotations

import logging
from typing import Dict, List, Optional
from ai.digital_twin.schema import InteractomeSnapshot

logger = logging.getLogger(__name__)


class SnapshotArchiveManager:
    """Stores and retrieves immutable, content-hashed graph snapshots."""

    def __init__(self) -> None:
        self._snapshots: Dict[str, InteractomeSnapshot] = {}

    def archive_snapshot(self, snapshot: InteractomeSnapshot) -> str:
        snapshot.compute_hash()
        self._snapshots[snapshot.snapshot_id] = snapshot
        logger.info(f"Archived snapshot {snapshot.snapshot_id} (hash: {snapshot.content_hash[:8]}).")
        return snapshot.content_hash

    def get_snapshot(self, snapshot_id: str) -> Optional[InteractomeSnapshot]:
        return self._snapshots.get(snapshot_id)

    def list_snapshots(self) -> List[InteractomeSnapshot]:
        return list(self._snapshots.values())
