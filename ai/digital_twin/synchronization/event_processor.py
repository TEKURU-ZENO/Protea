"""Data Ingestion Event Processor for digital twin synchronization."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List

logger = logging.getLogger(__name__)


@dataclass
class TwinUpdateEvent:
    event_id: str
    twin_id: str
    version_id: str
    event_type: str  # e.g. "NEW_OBSERVATION", "GRAPH_REVISION", "CALIBRATION"
    payload: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class TwinEventProcessor:
    """Event bus delivering synchronization notifications to active digital twins."""

    def __init__(self) -> None:
        self._handlers: Dict[str, List[Callable[[TwinUpdateEvent], None]]] = {}

    def subscribe(self, event_type: str, handler: Callable[[TwinUpdateEvent], None]) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def publish(self, event: TwinUpdateEvent) -> None:
        logger.info(f"Publishing event {event.event_id} ({event.event_type}) for twin {event.twin_id}")
        handlers = self._handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Event handler failed: {e}")
